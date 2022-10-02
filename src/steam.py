import requests
from bs4 import BeautifulSoup


STEAM_LIBRARY_ROOT = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
STEAM_TAGS_ROOT = "https://store.steampowered.com/app/"


def get_user_library(key, steamid):
    params = {
        "key": key,
        "steamid": steamid,
        "include_appinfo": "true",
        "include_played_free_games": "true",
        "format": "json"
    }
    r = requests.get(STEAM_LIBRARY_ROOT, params=params)

    if r.status_code != 200:
        return

    return [
        {
            "appid": game["appid"],
            "name": game["name"],
            "playtime": game["playtime_forever"]
        } for game in r.json()["response"]["games"]
    ]

def get_game_tags(appid):
    # bypass annoying age check
    headers = {
        "cookie": "birthtime=0; path=/; max-age=315360000"
    }
    r = requests.get(STEAM_TAGS_ROOT + str(appid), headers=headers)
    s = BeautifulSoup(r.content, "html.parser")
    tags = s.find_all("a", {"class": "app_tag"})
    return [tag.text.strip() for tag in tags]
