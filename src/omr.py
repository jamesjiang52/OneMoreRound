import os
import math
from pprint import pprint
from steam import *
from metacritic import *


def print_recommendations(game_scores):
    print("Based on the tags of the games you enjoy, you might also enjoy these games in your backlog:")
    for i in range(min(10, len(game_scores))):
        print("\t{:50} (Steam tag score: {:5.1f})".format(*game_scores[i]))


def main():
    pwd = os.path.dirname(__file__)
    cfg = [line.strip() for line in open("{}/cfg.txt".format(pwd), "r")]

    if cfg[0] != "### Steam API key ###" or cfg[3] != "## Steam user ID ###":
        print("cfg.txt has been incorrectly edited. Please restore a previous version.")
        exit(1)
    
    if cfg[1] == "<insert Steam API key here>":
        print("Must insert Steam API key in cfg.txt")
        exit(1)
    
    if cfg[4] == "<insert Steam user ID here>":
        print("Must insert Steam user ID in cfg.txt")
        exit(1)

    STEAM_API_KEY = cfg[1]
    STEAM_USER_ID = cfg[4]

    lib = get_user_library(STEAM_API_KEY, STEAM_USER_ID)
    if not lib:
        print("Invalid Steam API key or user ID")
        exit(1)
    
    # simple tag-based recommendation algorithm
    # a score is computed for every tag, indicating how much the user plays games associated with that tag
    # presumably, tags that appear more often in played games are more liked by the user
    # tags are also weighted by the ratio of the root of the game's playtime with the user's max playtime on a single game
    tag_dict = {}
    game_tags = {}
    max_playtime = max([game["playtime"] for game in lib])
    for game in lib:
        if game["playtime"] != 0:
            tags = get_game_tags(game["appid"])
            game_tags[game["appid"]] = tags
            weight = math.sqrt(game["playtime"])/math.sqrt(max_playtime)
            for tag in tags:
                tag_dict[tag] = weight if tag not in tag_dict else tag_dict[tag] + weight

    # get total tag scores of games in the backlog by summing up the individual scores of the game's tags
    max_tag_score = 0
    tag_scores = []
    for game in lib:
        if game["playtime"] == 0:
            tags = get_game_tags(game["appid"])
            score = sum([tag_dict[tag] for tag in tags if tag in tag_dict])
            tag_scores.append((game["name"], score))
            max_tag_score = max(max_tag_score, score)
        else:
            tags = game_tags[game["appid"]]
            score = sum([tag_dict[tag] for tag in tags if tag in tag_dict])
            max_tag_score = max(max_tag_score, score)

    # recommend games with the highest total tag scores
    tag_scores = [(score[0], score[1]*100/max_tag_score) for score in tag_scores]
    tag_scores.sort(key=lambda item: item[1], reverse=True)
    print_recommendations(tag_scores)

    exit(0)


if __name__ == "__main__":
    main()
