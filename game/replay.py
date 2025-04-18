import asyncio
import os

from funcy import first
from play import Game, Player


class LogPlayer(Player):
    def __init__(self, actions):
        self.actions_it = iter(actions)

    async def get_action(self, observation):
        return next(self.actions_it)

    async def end_game(self):
        pass


async def main():
    with open("./game.log") as log_file:
        log_lines = list(map(lambda line: line.strip(), log_file.readlines()))

    seed = first(map(
        lambda log_line: eval(log_line.split(":")[1]),
        filter(
            lambda log_line: log_line.startswith("seed:"),
            log_lines
        )
    ))

    player_0_actions = list(map(
        lambda action_line: eval(action_line.split(":")[1]),
        filter(
            lambda log_line: log_line.startswith("player-0 action:"),
            log_lines
        )
    ))

    player_1_actions = list(map(
        lambda action_line: eval(action_line.split(":")[1]),
        filter(
            lambda log_line: log_line.startswith("player-1 action:"),
            log_lines
        )
    ))

    with open(os.devnull, mode="w") as null_file:
        result = await Game(
            LogPlayer(player_0_actions),
            LogPlayer(player_1_actions),
            seed,
            True,
            null_file
        ).play()

    print(f"{result['player-0']}\t{result['player-1']}")

asyncio.run(main())
