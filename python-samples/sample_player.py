import numpy as np
import sys

from funcy import partial
from player import Player
from utility import get_enemy_observation, get_shortest_path, get_shortest_path_with_fence


class SamplePlayer(Player):
    def __init__(self, seed=None):
        print("*** SamplePlayer ***", file=sys.stderr)

    def get_longest_path_for_enemy_fence(self, observation):
        enemy_observation = get_enemy_observation(observation)

        max_distance = len(get_shortest_path(enemy_observation))
        fence = None

        for row, column, is_vertical in map(partial(map, int), zip(*np.where(np.array(enemy_observation[4]) == 0))):
            shortest_path = get_shortest_path_with_fence(enemy_observation, row, column, is_vertical)
            if shortest_path is None:
                continue

            distance = len(shortest_path)
            if distance > max_distance:
                fence = 7 - row, 7 - column, is_vertical
                max_distance = distance

        return fence

    def get_fence(self, observation):
        return self.get_longest_path_for_enemy_fence(observation)

    def get_force(self, observation):
        shortest_path = get_shortest_path(observation)

        if len(shortest_path) == 1:
            return [1, 0]

        r, c = shortest_path[1]

        px, py = observation[0]
        vx, vy = observation[1]

        return [c - 4 - px - vx, (r - 4) * -1 - py - vy]

    def get_action(self, observation):
        if observation[5] > 0 and observation[7] == 0:
            fence = self.get_fence(observation)
            if fence is not None:
                return 1, [0, 0], fence

        return 0, self.get_force(observation), (0, 0, 0)


if __name__ == "__main__":
    SamplePlayer().run()
