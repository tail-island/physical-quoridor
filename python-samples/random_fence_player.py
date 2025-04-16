import sys

from player import Player
from random import Random


class RandomFencePlayer(Player):
    def __init__(self, seed=None):
        print("*** RandomFencePlayer ***", file=sys.stderr)

        if seed is None:
            seed = Random().randint(0, 1_000)
            print(f"random seed: {seed}", file=sys.stderr)

        self.rng = Random(seed)

    def get_action(self, observation):
        return (
            1,
            [
                0.0,
                0.0
            ],
            (
                self.rng.randint(0, 7),
                self.rng.randint(0, 7),
                self.rng.randint(0, 1)
            )
        )


if __name__ == "__main__":
    RandomFencePlayer().run()
