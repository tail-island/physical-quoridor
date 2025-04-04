# from pettingzoo.test import parallel_api_test
# from physical_quoridor import PhysicalQuoridorEnv


# env = PhysicalQuoridorEnv(render_mode="human")
# parallel_api_test(env)


import numpy as np

from physical_quoridor import PhysicalQuoridorEnv
from time import sleep


env = PhysicalQuoridorEnv(render_mode="human")

for i in range(1_000):
    print(i)
    rng = np.random.default_rng(i)
    observations, _ = env.reset()

    observations, rewards, terminations, _, _ = env.step({
        0: (0, [1.0, 0.0]),
        1: (0, [1.0, 0.0])
    })

    observations, rewards, terminations, _, _ = env.step({
        0: (0, [1.0, 0.0]),
        1: (0, [1.0, 0.0])
    })

    while True:
        observations, rewards, terminations, _, _ = env.step({
            0: (0, rng.uniform(-1, 1, 2)) if rng.random() > 0.5 else (1, (rng.integers(0, 8), rng.integers(0, 8), rng.integers(0, 2))),
            1: (0, rng.uniform(-1, 1, 2)) if rng.random() > 0.5 else (1, (rng.integers(0, 8), rng.integers(0, 8), rng.integers(0, 2)))
        })

        if all(terminations.values()):
            print(rewards)
            break

        sleep(0.1)

    sleep(3)


# from physical_quoridor import PhysicalQuoridorEnv
# from time import sleep


# env = PhysicalQuoridorEnv(render_mode="human")
# observations, _ = env.reset()

# for i in range(1_000_000):
#     match i:
#         case 0:
#             observations, rewards, terminations, _, _ = env.step({
#                 0: (1, (3, 5, 1)),
#                 1: (1, (3, 3, 1))
#             })

#         case 1:
#             observations, rewards, terminations, _, _ = env.step({
#                 0: (1, (2, 6, 0)),
#                 1: (1, (2, 4, 0))
#             })

#         case 2:
#             observations, rewards, terminations, _, _ = env.step({
#                 0: (1, (4, 6, 0)),
#                 1: (1, (2, 4, 0))
#             })

#         case 10:
#             observations, rewards, terminations, _, _ = env.step({
#                 0: (1, (3, 7, 1)),
#                 1: (1, (2, 4, 0))
#             })

#         case _:
#             forces = [None, None]

#             for i in range(2):
#                 match observations[i][0][0][0]:
#                     case x if x < -0.5:
#                         forces[i] = (1.0, -0.1)
#                     case x if x < 0.5:
#                         forces[i] = (0.1, 0.1)
#                     case _:
#                         forces[i] = (0.1, -0.3)

#             observations, rewards, terminations, _, _ = env.step({
#                 0: (0, forces[0]),
#                 1: (0, forces[1])
#             })

#     if all(terminations.values()):
#         print(rewards)
#         break

#     sleep(0.1)

# sleep(3)
