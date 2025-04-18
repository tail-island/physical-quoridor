import sys

from player import Player


class DoNothingPlayer(Player):
    def __init__(self, seed=None):
        print("*** DoNothingPlayer ***", file=sys.stderr)

    def get_action(self, observation):
        return (0, [0.0, 0.0], (0, 0, 0))


if __name__ == "__main__":
    DoNothingPlayer().run()
