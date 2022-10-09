import os
import math
import tkinter as tk
from tkinter import ttk
from steam import *
from metacritic import *
from hltb import *


def display_user_library(event):
    global lib

    STEAM_API_KEY = api_key_field.get()
    STEAM_USER_ID = steam_id_field.get()

    lib = get_user_library(STEAM_API_KEY, STEAM_USER_ID)
    if not lib:
        print("Invalid Steam API key or user ID")
        exit(1)

    library.delete(*library.get_children())
    for i in range(len(lib)):
        library.insert(parent="", index="end", iid=i, text="", values=(lib[i]["name"], "{:.1f} hours".format(lib[i]["playtime"]/60)))


def display_recommendations(event):
    STEAM_TAG_WEIGHT = tag_select_int.get()
    META_SCORE_WEIGHT = metacritic_select_int.get()
    USER_SCORE_WEIGHT = 1 - META_SCORE_WEIGHT if META_SCORE_WEIGHT != 0 else 0
    GAME_TIME_WEIGHT = playtime_select_int.get()

    count_0 = [STEAM_TAG_WEIGHT, META_SCORE_WEIGHT, GAME_TIME_WEIGHT].count(0)
    if count_0 != 3:
        STEAM_TAG_WEIGHT /= (3 - count_0)
        META_SCORE_WEIGHT /= (3 - count_0)
        USER_SCORE_WEIGHT /= (3 - count_0)
        GAME_TIME_WEIGHT /= (3 - count_0)

    # simple tag-based recommendation algorithm
    # a score is computed for every Steam tag, indicating how much the user plays games associated with that tag
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

    # get total tag scores of games in the backlog by summing up the individual scores of the game's Steam tags
    # also get meta (aggregate review) and user scores from Metacritic, and times to beat from HowLongToBeat (longer is better, up to 100 hours)
    max_tag_score = 0
    game_scores = []
    max_playtime = 0
    for game in lib:
        if game["playtime"] == 0:
            tags = get_game_tags(game["appid"])
            tag_score = sum([tag_dict[tag] for tag in tags if tag in tag_dict])
            meta_score, user_score = get_game_ratings(game["name"])
            time = get_game_time(game["name"])
            max_playtime = min(100, max(time, max_playtime))
            game_scores.append((game["name"], tag_score, meta_score, user_score, time))
            max_tag_score = max(max_tag_score, tag_score)
        else:
            tags = game_tags[game["appid"]]
            tag_score = sum([tag_dict[tag] for tag in tags])
            max_tag_score = max(max_tag_score, tag_score)

    # choose games to recommend by multiplying all scores with each score's respective weight
    game_scores = [(score[0], score[1]*100/max_tag_score, score[2], score[3], score[4]) for score in game_scores]
    game_scores.sort(key=lambda item: STEAM_TAG_WEIGHT*item[1] + META_SCORE_WEIGHT*item[2] + USER_SCORE_WEIGHT*item[3] + GAME_TIME_WEIGHT*(item[4]/max_playtime), reverse=True)

    recommend.delete(*recommend.get_children())
    for i in range(min(10, len(game_scores))):
        recommend.insert(parent="", index="end", iid=i, text="", values=(game_scores[i][0], "{:.1f}".format(game_scores[i][1]), *game_scores[i][2:4], "{:.1f} hours".format(game_scores[i][4])))


def main():
    global api_key_field
    global steam_id_field
    global library
    global tag_select_int
    global metacritic_select_int
    global playtime_select_int
    global recommend

    window = tk.Tk()
    window.title("OneMoreRound")

    cfg_frame = tk.Frame()
    cfg_frame.grid(row=0, column=0)

    api_key_label = tk.Label(master=cfg_frame, text="Steam API key:")
    api_key_label.grid(row=0, column=0)
    api_key_field = tk.Entry(master=cfg_frame, width=40)
    api_key_field.grid(row=0, column=1)

    steam_id_label = tk.Label(master=cfg_frame, text="Steam ID:")
    steam_id_label.grid(row=1, column=0)
    steam_id_field = tk.Entry(master=cfg_frame, width=40)
    steam_id_field.grid(row=1, column=1)

    lib_frame = tk.Frame()
    lib_frame.grid(row=1, column=0)

    get_lib_button = tk.Button(master=lib_frame, text="Get Steam library")
    get_lib_button.grid(row=0, column=0)
    get_lib_button.bind("<Button-1>", display_user_library)

    library = ttk.Treeview(master=lib_frame, height=20)
    library["columns"] = ("name", "playtime")
    library.column("#0", width=0, stretch=tk.NO)
    library.column("name", anchor=tk.CENTER, width=200)
    library.column("playtime", anchor=tk.CENTER, width=80)
    library.heading("#0", text="", anchor=tk.CENTER)
    library.heading("name", text="Game", anchor=tk.CENTER)
    library.heading("playtime", text="Playtime", anchor=tk.CENTER)
    library.grid(row=1, column=0)

    lib_scrollx = tk.Scrollbar(master=lib_frame, orient=tk.HORIZONTAL, command=library.xview)
    lib_scrolly = tk.Scrollbar(master=lib_frame, orient=tk.VERTICAL, command=library.yview)
    lib_scrollx.grid(row=1, column=0, sticky="ews")
    lib_scrolly.grid(row=1, column=1, sticky="nse")
    library.configure(xscroll=lib_scrollx.set, yscroll=lib_scrolly.set)

    select_frame = tk.Frame()
    select_frame.grid(row=1, column=1)

    tag_select_label = tk.Label(master=select_frame, text="Select Steam tag option:")
    tag_select_label.pack()
    tag_select_int = tk.IntVar()
    tk.Radiobutton(master=select_frame, text="Give me something I'd like!", variable=tag_select_int, value=1).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="Give me something new!", variable=tag_select_int, value=-1).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="I don't care about Steam tags", variable=tag_select_int, value=0).pack(anchor=tk.W)
    tag_select_int.set(0)

    metacritic_select_label = tk.Label(master=select_frame, text="Select Metacritic option:")
    metacritic_select_label.pack()
    metacritic_select_int = tk.DoubleVar()
    tk.Radiobutton(master=select_frame, text="Higher meta score", variable=metacritic_select_int, value=0.8).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="Higher user score", variable=metacritic_select_int, value=0.2).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="Weigh both Metacritic scores equally", variable=metacritic_select_int, value=0.5).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="I don't care about Metacritic scores", variable=metacritic_select_int, value=0).pack(anchor=tk.W)
    metacritic_select_int.set(0)

    playtime_select_label = tk.Label(master=select_frame, text="Select completion time option:")
    playtime_select_label.pack()
    playtime_select_int = tk.IntVar()
    tk.Radiobutton(master=select_frame, text="Give me a long one!", variable=playtime_select_int, value=1).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="Give me something short and sweet!", variable=playtime_select_int, value=-1).pack(anchor=tk.W)
    tk.Radiobutton(master=select_frame, text="I don't care about completion time", variable=playtime_select_int, value=0).pack(anchor=tk.W)
    playtime_select_int.set(0)

    recommend_frame = tk.Frame()
    recommend_frame.grid(row=1, column=2)

    get_recommend_button = tk.Button(master=recommend_frame, text="Get backlog recommendations!")
    get_recommend_button.grid(row=0, column=0)
    get_recommend_button.bind("<Button-1>", display_recommendations)

    recommend = ttk.Treeview(master=recommend_frame, height=20)
    recommend["columns"] = ("name", "tag score", "meta score", "user score", "completion time")
    recommend.column("#0", width=0, stretch=tk.NO)
    recommend.column("name", anchor=tk.CENTER, width=200)
    recommend.column("tag score", anchor=tk.CENTER, width=100)
    recommend.column("meta score", anchor=tk.CENTER, width=80)
    recommend.column("user score", anchor=tk.CENTER, width=80)
    recommend.column("completion time", anchor=tk.CENTER, width=100)
    recommend.heading("#0", text="", anchor=tk.CENTER)
    recommend.heading("name", text="Game", anchor=tk.CENTER)
    recommend.heading("tag score", text="Steam tag score", anchor=tk.CENTER)
    recommend.heading("meta score", text="Meta score", anchor=tk.CENTER)
    recommend.heading("user score", text="User score", anchor=tk.CENTER)
    recommend.heading("completion time", text="Completion time", anchor=tk.CENTER)
    recommend.grid(row=1, column=0)

    recommend_scrollx = tk.Scrollbar(master=recommend_frame, orient=tk.HORIZONTAL, command=recommend.xview)
    recommend_scrolly = tk.Scrollbar(master=recommend_frame, orient=tk.VERTICAL, command=recommend.yview)
    recommend_scrollx.grid(row=1, column=0, sticky="ews")
    recommend_scrolly.grid(row=1, column=1, sticky="nse")
    recommend.configure(xscroll=recommend_scrollx.set, yscroll=recommend_scrolly.set)

    window.mainloop()


if __name__ == "__main__":
    main()
