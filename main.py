import requests
import sys
import click
from configparser import ConfigParser

@click.command()
@click.option('-k', '--key', "key", help="Steam API key required to use the service. This option can not be used in the case there is already one key saved.")
@click.option('-u', '--user', "steam_id", required=True, help="Steam ID of the user to be searched. Mandatory option.")
@click.option('-s', '--save', "save", is_flag=True, help="Option switch to save the current key in the app. Will replace an existing one.")
def leApp(key, steam_id, save):
    # key = "0BE6D41C39906AD3D7E1085F310BBC77"
    # key = sys.argv[1]
    # steam_id = "76561197990642328"
    # steam_id = sys.argv[2]
    config = ConfigParser()
    config.read("config.ini")
    
    if save:
        if not key:
            print("Key argument is needed to save the key! Exiting!")
            sys.exit()
        config.set("main", "key", key)
        with open("config.ini", "w") as f:
            config.write(f)

    if not key:
        key = config.get("main", "key")
        if not key:
            print("Steam API key not found in argument or config.ini file. Exiting.")
            sys.exit()

    username_payload = {"key": key, "steamids": steam_id}
    resp = requests.get(
        "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002", params=username_payload)
    # print(resp.text)
    if resp.status_code == 403:
        print("Invalid Steam API key!")
        sys.exit()

    resp.raise_for_status()

    players_list = resp.json()["response"]["players"]

    if len(players_list) == 0:
        print("No players have been found for that steam ID")
        sys.exit()

    username = players_list[0]["personaname"]

    gamestats_payload = {"key": key, "steamid": steam_id,
                         "include_played_free_games": 1, "include_appinfo": 1}
    resp = requests.get(
        "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001", params=gamestats_payload)

    resp.raise_for_status()

    # json = resp.json()
    # print(json)
    sum_mins = 0
    max_mins = 0
    most_played_game = ""
    for game in resp.json()["response"]["games"]:
        mins = game["playtime_forever"]
        sum_mins += mins
        if mins > max_mins:
            max_mins = mins
            most_played_game = game["name"]

    print(f'''{username} has wasted {sum_mins} minutes, the equivalent of {sum_mins/60:.2f} hours or {sum_mins/60/24:.2f} days 
    of his/her life playing video games on Steam. Mostly by playing {most_played_game} for {max_mins/60:.2f} hours.''')

    recently_payload = {"key": key, "steamid": steam_id}
    resp = requests.get(
        "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001", params=recently_payload)

    resp.raise_for_status()

    response = resp.json()["response"]

    if response["total_count"] > 0:

        games_set = set()
        sum_2week_time = 0
        for game in response["games"]:
            games_set.add(game["name"])
            sum_2week_time += game["playtime_2weeks"]
        print(
            f"Has been lately (2 weeks) playing: \n{', '.join(games_set)} for {sum_2week_time/60:.2f} hours.")
    else:
        print("Has not been playing anything lately.")


if __name__ == '__main__':
    leApp()
