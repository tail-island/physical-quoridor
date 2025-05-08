import sys

from player import Player
from random import Random


class RandomPlayer(Player):
    def __init__(self, seed=None):
        print("*** RandomPlayer ***", file=sys.stderr)

        if seed is None:
            seed = Random().randint(0, 1_000)
            print(f"random seed: {seed}", file=sys.stderr)

        self.rng = Random(seed)
        self.step = 0

    def get_action(self, observation):
        print(observation, file=sys.stderr)

        match self.step:
            case 0:
                action = 0, [0.5, 0.0], (0, 0, 0)
            case 1:
                action = 0, [0.5, 0.0], (0, 0, 0)
            case 2:
                action = 0, [0.5, 0.0], (0, 0, 0)
            case 3:
                action = 0, [0.5, 0.0], (0, 0, 0)
            case _:
                action = (
                    self.rng.randint(0, 1),
                    [
                        (self.rng.random() - 0.5),
                        (self.rng.random() - 0.5),
                    ],
                    (
                        self.rng.randint(0, 7),
                        self.rng.randint(0, 7),
                        self.rng.randint(0, 1)
                    )
                )

        print(action, file=sys.stderr)

        self.step += 1

        return action


if __name__ == "__main__":
    RandomPlayer().run()
