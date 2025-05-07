import sys

from player import Player


class DoNothingPlayer(Player):
    def __init__(self, seed=None):
        print("*** DoNothingPlayer ***", file=sys.stderr)


if __name__ == "__main__":
    DoNothingPlayer().run()
