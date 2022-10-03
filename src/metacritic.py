import re
import requests
from bs4 import BeautifulSoup


METACRITIC_ROOT = "http://metacritic.com/game/pc/"


def get_game_ratings(name):
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace("& ", "")
    name = re.sub("[^a-z\d\?!\-]+", "", name)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    r = requests.get(METACRITIC_ROOT + name, headers=headers)
    s = BeautifulSoup(r.content, "html.parser")
    #print(s.prettify)
    meta_score = s.find_all("div", {"class": "metascore_w xlarge game positive"})[0]
    user_score = s.find_all("div", {"class": "metascore_w user large game positive"})[0]

    return int(meta_score.text.strip()), int(float(user_score.text.strip())*10)
