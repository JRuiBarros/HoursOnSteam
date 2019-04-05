import requests
import sys

# key = "0BE6D41C39906AD3D7E1085F310BBC77"
key = sys.argv[1]
# steamid = "76561197990642328"
steamid = sys.argv[2]

username_payload = {"key": key, "steamids": steamid}
resp = requests.get(
    "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002", params=username_payload)
# print(resp.text)
username = resp.json()["response"]["players"][0]["personaname"]

gamestats_payload = {"key": key, "steamid": steamid,
                     "include_played_free_games": 1, "include_appinfo": 1}
resp = requests.get(
    "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001", params=gamestats_payload)
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

recently_payload = {"key": key, "steamid": steamid}
resp = requests.get(
    "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001", params=recently_payload)
response = resp.json()["response"]

if response["total_count"] > 0:

    games_set = set()
    sum_2week_time = 0
    for game in response["games"]:
        games_set.add(game["name"])
        sum_2week_time += game["playtime_2weeks"]
    print(f"Has been lately (2 weeks) playing: \n{', '.join(games_set)} for {sum_2week_time/60:.2f} hours.")