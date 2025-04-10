# from pettingzoo.test import parallel_api_test
# from physical_quoridor import PhysicalQuoridorEnv


# env = PhysicalQuoridorEnv(render_mode="human")
# parallel_api_test(env)

########

from physical_quoridor import PhysicalQuoridorEnv
from time import sleep


env = PhysicalQuoridorEnv(render_mode="human")
observations, _ = env.reset()

for agent in range(1_000_000):
    match agent:
        case 0:
            observations, rewards, terminations, _, _ = env.step({
                "player-0": (1, [0, 0], (3, 3, 1)),
                "player-1": (1, [0, 0], (3, 3, 1))
            })

        case 1:
            observations, rewards, terminations, _, _ = env.step({
                "player-0": (1, [0, 0], (2, 4, 0)),
                "player-1": (1, [0, 0], (2, 4, 0))
            })

        case _:
            forces = {}

            for agent in env.agents:
                match observations[agent][0][0]:
                    case x if x < -0.5:
                        forces[agent] = (1.0, -0.1)
                    case x if x < 0.5:
                        forces[agent] = (0.1, 1.0)
                    case _:
                        forces[agent] = (1.0, -0.1)

            observations, rewards, terminations, _, _ = env.step({
                "player-0": (0, forces["player-0"], (0, 0, 0)),
                "player-1": (0, forces["player-1"], (0, 0, 0))
            })

    if all(terminations.values()):
        print(rewards)
        break

    sleep(0.1)

sleep(3)
