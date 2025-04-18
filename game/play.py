import asyncio
import json
import numpy as np
import sys

from argparse import ArgumentParser
from physical_quoridor import PhysicalQuoridorEnv
from random import Random
from time import sleep, perf_counter


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
    def __init__(self, player_0, player_1, seed, wait, log_file):
        if seed is None:
            seed = Random().randrange(1, 1_000)

        print(f"seed: {seed}", file=log_file)

        self.players = {
            "player-0": player_0,
            "player-1": player_1
        }
        self.seed = seed
        self.wait = wait
        self.log_file = log_file

    async def terminate(self):
        for player in self.players.values():
            try:
                await player.end_game()
            except Exception:
                pass

    async def play(self):
        env = PhysicalQuoridorEnv(render_mode="human")

        observations, _ = env.reset(seed=self.seed)

        while True:
            step_starting_time = perf_counter()

            actions = {}
            for name, player in self.players.items():
                try:
                    action = await player.get_action(observations[name])
                    print(f"{name}: {action}", file=self.log_file)

                    actions[name] = action

                except asyncio.TimeoutError:
                    print(f"{name}: time out...", file=sys.stderr)

                    await self.terminate()
                    return dict(map(lambda key: (key, 1.0 if key != name else -1.0), self.players.keys()))

                except Exception as e:
                    print(f"{name}: something wrong...", file=sys.stderr)
                    print(e, file=sys.stderr)

                    await self.terminate()
                    return dict(map(lambda key: (key, 1.0 if key != name else -1.0), self.players.keys()))

            observations, rewards, terminations, _, _ = env.step(actions)

            if any(terminations.values()):
                await self.terminate()
                return rewards

            if self.wait:
                sleep(max(step_starting_time + 0.1 - perf_counter(), 0))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("player_0")
    parser.add_argument("player_1")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--wait", action="store_true")

    args = parser.parse_args()

    async def main(player_0_command, player_1_command, seed, wait):
        with open("./game.log", mode="w") as log_file:
            result = await Game(
                await create_player(player_0_command, open("./player-0.log", mode="w")),
                await create_player(player_1_command, open("./player-1.log", mode="w")),
                seed,
                wait,
                log_file
            ).play()

        print(f"{result['player-0']}\t{result['player-1']}")

    asyncio.run(main(args.player_0, args.player_1, args.seed, args.wait))
