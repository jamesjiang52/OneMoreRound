from howlongtobeatpy import HowLongToBeat


def get_game_time(name):
    r = HowLongToBeat().search(name)

    if not r:
        print("Can't find HowLongToBeat times for game:", name)
        return 0

    r = max(r, key = lambda x: x.similarity)
    return r.all_styles
