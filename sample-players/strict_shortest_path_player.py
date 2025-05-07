import sys

from player import Player
from utility import get_shortest_path


class StrictShortestPathPlayer(Player):
    def __init__(self, seed=None):
        print("*** StrictShortestPathPlayer ***", file=sys.stderr)

    def get_action(self, observation):
        shortest_path = get_shortest_path(observation)

        if len(shortest_path) == 1:
            return 0, [1, 0], (0, 0, 0)

        r, c = shortest_path[1]

        px, py = observation[0]
        vx, vy = observation[1]

        return 0, [c - 4 - px - vx, (r - 4) * -1 - py - vy], (0, 0, 0)


if __name__ == "__main__":
    StrictShortestPathPlayer().run()
