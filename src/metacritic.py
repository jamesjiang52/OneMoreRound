import re
import requests
from bs4 import BeautifulSoup

# requests throws SSL errors for Metacritic for some reason,
# so turn off verification and ignore the warnings that appear as a result
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


METACRITIC_ROOT = "http://metacritic.com/game/pc/"


def get_game_ratings(name):
    name_orig = name
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace("& ", "")
    name = re.sub("[^a-z\d\?!\-]+", "", name)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    r = requests.get(METACRITIC_ROOT + name, headers=headers, verify=False)
    s = BeautifulSoup(r.content, "html.parser")

    try:
        meta_scores = set(s.find_all("div", {"class": "metascore_w"}))
        game = set(s.find_all("div", {"class": "game"}))
        user = set(s.find_all("div", {"class": "user"}))
        xlarge = set(s.find_all("div", {"class": "xlarge"}))
        large = set(s.find_all("div", {"class": "large"}))

        meta_score = int(list(meta_scores.intersection(game, xlarge))[0].text.strip())
        user_score = int(float(list(meta_scores.intersection(game, large, user))[0].text.strip())*10)
    except:
        print("Can't find Metacritic reviews for game:", name_orig)
        return 0, 0

    return meta_score, user_score
