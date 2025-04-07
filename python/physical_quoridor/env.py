import cv2 as cv
import gymnasium
import numpy as np
import pettingzoo
import pygame

from copy import copy
from functools import lru_cache
from .physical_quoridor import PhysicalQuoridor


class PhysicalQuoridorEnv(pettingzoo.ParallelEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "PhysicalQuoridor"
    }

    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode
        self.screen = None
        self.surface = None

        self.possible_agents = list(range(2))

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.physical_quoridor = PhysicalQuoridor(seed if seed is not None else 1234)

        return (
            {
                0: (np.array([-4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.array([4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.zeros((8, 8, 2), dtype=np.int8), 10, 10),
                1: (np.array([-4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.array([4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.zeros((8, 8, 2), dtype=np.int8), 10, 10)
            },
            {
                0: {},
                1: {}
            }
        )

    def step(self, actions):
        actions = dict(zip(
            actions.keys(),
            map(
                lambda action: (action[0], action[1].tolist() if isinstance(action[1], np.ndarray) else list(action[1]), tuple(action[2])),
                actions.values()
            )
        ))

        observations, rewards, terminations = self.physical_quoridor.step(list(map(
            lambda i: actions[i],
            sorted(actions.keys())
        )))

        if any(terminations):
            self.agents = []

        if self.render_mode in {"human", "rgb_array"}:
            self.render(observations[0])

        return dict(enumerate(observations)), dict(enumerate(rewards)), dict(enumerate(terminations)), {0: False, 1: False}, {0: {}, 1: {}}

    def get_board_image(self, observation):
        result = np.zeros([900, 900, 3], dtype=np.uint8)

        for i in range(1, 8 + 1):
            cv.line(result, [i * 100, 0], [i * 100, 899], [128, 128, 128], 1)

        for i in range(1, 8 + 1):
            cv.line(result, [0, i * 100], [899, i * 100], [128, 128, 128], 1)

        for row, column, is_vertical in zip(*np.where(np.array(observation[4]))):
            center_x = (column + 1) * 100
            center_y = (row + 1) * 100
            width = 220
            height = 20

            if is_vertical:
                width, height = height, width

            cv.rectangle(result, (center_x - width // 2, center_y - height // 2), (center_x + width // 2, center_y + height // 2), (255, 255, 255), -1)

        [pawn_0_x, pawn_0_y] = observation[0]
        [pawn_1_x, pawn_1_y] = observation[2]

        cv.circle(result, [int((pawn_0_x + 4.5) * 100), int((-pawn_0_y + 4.5) * 100)], 20, [255, 127, 127], -1)
        cv.circle(result, [int((pawn_1_x + 4.5) * 100), int((-pawn_1_y + 4.5) * 100)], 20, [127, 127, 255], -1)

        result = cv.cvtColor(result, cv.COLOR_BGR2RGB)

        return result

    def render(self, observation):
        if self.render_mode not in {"human", "rgb_array"}:
            gymnasium.logger.warn("Please set 'human' or 'rgb_array' to render_mode.")

        image = self.get_board_image(observation)

        if self.render_mode == "human":
            if self.screen is None:
                pygame.init()
                pygame.display.set_caption("Physical Quoridor")

                self.screen = pygame.display.set_mode((900, 900))
                self.surface = pygame.surfarray.make_surface(image)

            for event in pygame.event.get():
                pass

            pygame.surfarray.blit_array(self.surface, image.swapaxes(0, 1))
            self.screen.blit(self.surface, [0, 0])
            pygame.display.update()
        else:
            return image

    @lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Tuple((
            gymnasium.spaces.Discrete(2),                                 # 移動なら0、フェンス設置なら1
            gymnasium.spaces.Box(-1, 1, shape=[2], dtype=np.float32),     # 移動
            gymnasium.spaces.Tuple((                                      # フェンス設置
                gymnasium.spaces.Discrete(8),                             # row
                gymnasium.spaces.Discrete(8),                             # column
                gymnasium.spaces.Discrete(2)                              # 横なら0、縦なら1
            ))
        ))

    @lru_cache(maxsize=None)
    def observation_space(self, agent):
        return gymnasium.spaces.Tuple((
            gymnasium.spaces.Box(-5, 5, shape=[2], dtype=np.float32),    # 自分の駒の位置
            gymnasium.spaces.Box(-20, 20, shape=[2], dtype=np.float32),  # 自分の駒の速度
            gymnasium.spaces.Box(-5, 5, shape=[2], dtype=np.float32),    # 敵の駒の位置
            gymnasium.spaces.Box(-20, 20, shape=[2], dtype=np.float32),  # 敵の駒の速度
            gymnasium.spaces.MultiBinary([8, 8, 2]),                     # フェンスの有無
            gymnasium.spaces.Discrete(11),                               # 自分の残りフェンス数
            gymnasium.spaces.Discrete(11)                                # 敵の残りフェンス数
        ))


def convert_to_box(value, min_value, max_value):
    return value * (max_value - min_value) + min_value


def convert_to_discrete(value, n):
    return int(round(convert_to_box(value, 0 - 0.5, n - 0.5)))


def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)


class PhysicalQuoridorEnv_(PhysicalQuoridorEnv):
    @classmethod
    def convert_actions(cls, actions):
        return dict(zip(
            actions.keys(),
            map(
                lambda action: (
                    convert_to_discrete(action[0], 2),
                    [
                        convert_to_box(action[1], -1, 1),
                        convert_to_box(action[2], -1, 1)
                    ],
                    (
                        convert_to_discrete(action[3], 8),
                        convert_to_discrete(action[4], 8),
                        convert_to_discrete(action[5], 2),
                    )
                ),
                actions.values()
            )
        ))

    @classmethod
    def convert_observations(cls, observations):
        return dict(zip(
            observations.keys(),
            map(
                lambda observation: [
                    normalize(observation[0][0], -5, 5),
                    normalize(observation[0][1], -5, 5),
                    normalize(observation[1][0], -20, 20),
                    normalize(observation[1][1], -20, 20),

                    normalize(observation[2][0], -5, 5),
                    normalize(observation[2][1], -5, 5),
                    normalize(observation[3][0], -20, 20),
                    normalize(observation[3][1], -20, 20),

                    *np.asarray(np.ravel(observation[4]), np.float32),

                    normalize(observation[5], 0, 10),
                    normalize(observation[6], 0, 10)
                ],
                observations.values()
            )
        ))

    def reset(self, seed=None, options=None):
        observations, infos = super().reset(seed=seed, options=options)

        return self.convert_observations(observations), infos

    def step(self, actions):
        observations, rewards, terminations, truncations, infos = super().step(self.convert_actions(actions))

        return self.convert_observations(observations), rewards, terminations, truncations, infos

    @lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Box(0, 1, shape=[6], dtype=np.float32)

    @lru_cache(maxsize=None)
    def observation_space(self, agent):
        return gymnasium.spaces.Box(0, 1, [2 + 2 + 2 + 2 + 8 * 8 * 2 + 1 + 1], dtype=np.float32)
