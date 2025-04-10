# from pettingzoo.test import parallel_api_test
# from physical_quoridor import PhysicalQuoridorEnv


# env = PhysicalQuoridorEnv(render_mode="human")
# parallel_api_test(env)


# import numpy as np

# from physical_quoridor import PhysicalQuoridorEnv
# from time import sleep


# env = PhysicalQuoridorEnv(render_mode="human")

# for i in range(1_000):
#     print(i)
#     rng = np.random.default_rng(i)
#     observations, _ = env.reset()

#     observations, rewards, terminations, _, _ = env.step({
#         0: (0, [1.0, 0.0], (0, 0, 0)),
#         1: (0, [1.0, 0.0], (0, 0, 0))
#     })

#     observations, rewards, terminations, _, _ = env.step({
#         0: (0, [1.0, 0.0], (0, 0, 0)),
#         1: (0, [1.0, 0.0], (0, 0, 0))
#     })

#     while True:
#         observations, rewards, terminations, _, _ = env.step({
#             0: (0, rng.uniform(-1, 1, 2), (0, 0, 0)) if rng.random() > 0.5 else (1, [0.0, 0.0], (rng.integers(0, 8), rng.integers(0, 8), rng.integers(0, 2))),
#             1: (0, rng.uniform(-1, 1, 2), (0, 0, 0)) if rng.random() > 0.5 else (1, [0.0, 0.0], (rng.integers(0, 8), rng.integers(0, 8), rng.integers(0, 2)))
#         })

#         if all(terminations.values()):
#             print(rewards)
#             break

#         sleep(0.1)

#     sleep(3)


# import numpy as np

# from physical_quoridor import PhysicalQuoridorEnv_
# from time import sleep


# env = PhysicalQuoridorEnv_(render_mode="human")

# for i in range(1_000):
#     print(i)
#     rng = np.random.default_rng(i)
#     observations, _ = env.reset()

#     observations, rewards, terminations, _, _ = env.step({
#         0: (0, 1.0, 0.0, 0, 0, 0),
#         1: (0, 1.0, 0.0, 0, 0, 0)
#     })

#     observations, rewards, terminations, _, _ = env.step({
#         0: (0, 1.0, 0.0, 0, 0, 0),
#         1: (0, 1.0, 0.0, 0, 0, 0)
#     })

#     while True:
#         observations, rewards, terminations, _, _ = env.step({
#             0: rng.uniform(0, 1, 6),
#             1: rng.uniform(0, 1, 6)
#         })

#         if all(terminations.values()):
#             print(rewards)
#             break

#         sleep(0.1)

#     sleep(3)


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
                        forces[agent] = (0.1, 0.5)
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
