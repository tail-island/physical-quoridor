import asyncio
import json
import numpy as np
import sys

from argparse import ArgumentParser
from physical_quoridor import PhysicalQuoridorEnv
from time import sleep


TIMEOUT = 5


def to_tuple(items):
    return tuple(map(lambda item: item.tolist() if isinstance(item, np.ndarray) else item, items))


class Player:
    def __init__(self, process, log_file):
        self.process = process
        self.log_file = log_file

    async def get_response(self, request):
        self.process.stdin.write((json.dumps(request) + "\n").encode("utf-8"))
        await self.process.stdin.drain()

        return json.loads((await asyncio.wait_for(self.process.stdout.readline(), TIMEOUT)).decode("utf-8"))

    async def get_action(self, observation):
        return await self.get_response({
            "command": "get_action",
            "observation": to_tuple(observation)
        })

    async def end_game(self):
        await self.get_response({
            "command": "end_game"
        })

        try:
            await asyncio.wait_for(self.process.communicate(), TIMEOUT)
        except asyncio.TimeoutError:
            self.process.terminate()

        self.log_file.close()


async def create_player(command, log_file):
    return Player(await asyncio.create_subprocess_shell(command, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=log_file), log_file)


class Game:
    def __init__(self, player_0, player_1, wait):
        self.players = {
            "player-0": player_0,
            "player-1": player_1
        }
        self.wait = wait

    async def terminate(self):
        for player in self.players.values():
            await player.end_game()

    async def play(self):
        env = PhysicalQuoridorEnv(render_mode="human")

        observations, _ = env.reset()

        while True:
            actions = {}
            for name, player in self.players.items():
                try:
                    actions[name] = await player.get_action(observations[name])

                except asyncio.TimeoutError:
                    print(f"{name}: time out...", file=sys.stderr)

                    await self.terminate()
                    return dict(map(lambda key: (key, 1.0 if key != name else -1.0), self.players.keys()))

                except Exception:
                    print("f{name}: something wring...")

                    await self.terminate()
                    return dict(map(lambda key: (key, 1.0 if key != name else -1.0), self.players.keys()))

            observations, rewards, terminations, _, _ = env.step(actions)

            if any(terminations.values()):
                await self.terminate()
                return rewards

            if self.wait:
                sleep(0.1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("player_0")
    parser.add_argument("player_1")
    parser.add_argument("--wait", action="store_true")

    args = parser.parse_args()

    async def main(player_0_command, player_1_command, wait):
        result = await Game(
            await create_player(player_0_command, open("./player-0.log", mode="w")),
            await create_player(player_1_command, open("./player-1.log", mode="w")),
            wait
        ).play()

        print(f"{result['player-0']}\t{result['player-1']}")

    asyncio.run(main(args.player_0, args.player_1, args.wait))
