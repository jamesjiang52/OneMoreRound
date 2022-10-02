import requests
from bs4 import BeautifulSoup
from pprint import pprint


API_KEY = <placeholder>
STEAM_ID = <placeholder>


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
        print("Invalid Steam ID")
        return
    
    return r.json()["response"]


def get_game_tags(appid):
    # bypass annoying age check
    headers = {
        "cookie": "birthtime=0; path=/; max-age=315360000"
    }
    r = requests.get(STEAM_TAGS_ROOT + str(appid), headers=headers)
    s = BeautifulSoup(r.content, "html.parser")
    tags = s.find_all("a", {"class": "app_tag"})
    return [tag.text.strip() for tag in tags]


if __name__ == "__main__":
    #pprint(get_user_library(API_KEY, STEAM_ID))
    print(get_game_tags(72850))
