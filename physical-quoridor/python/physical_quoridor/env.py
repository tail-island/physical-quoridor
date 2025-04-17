import cv2 as cv
import gymnasium
import numpy as np
import pettingzoo
import pygame

from copy import copy
from functools import lru_cache
from funcy import repeat
from itertools import starmap
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

        self.possible_agents = ["player-0", "player-1"]

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.physical_quoridor = PhysicalQuoridor(seed if seed is not None else 1234)

        return map(
            lambda values: dict(zip(self.agents, values)),
            (
                repeat((np.array([-4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.array([4.0, 0.0], dtype=np.float32), np.array([0.0, 0.0], dtype=np.float32), np.zeros((8, 8, 2), dtype=np.int8), 10, 10, 0, 0), len(self.agents)),
                repeat({}, len(self.agents))
            )
        )

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
        image = self.get_board_image(observation)

        if self.render_mode == "rgb_array":
            return image

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

    def step(self, actions):
        actions = dict(starmap(
            lambda agent, action: (
                agent,
                (action[0], action[1].tolist() if isinstance(action[1], np.ndarray) else list(action[1]), tuple(action[2]))
            ),
            actions.items()
        ))
        action_agents = list(sorted(actions.keys()))

        observations, rewards, terminations = self.physical_quoridor.step(list(map(
            lambda action_agent: actions[action_agent],
            action_agents
        )))

        observations = list(map(
            lambda observation: (
                np.array(observation[0], dtype=np.float32),
                np.array(observation[1], dtype=np.float32),
                np.array(observation[2], dtype=np.float32),
                np.array(observation[3], dtype=np.float32),
                np.array(observation[4], dtype=np.int8),
                observation[5],
                observation[6],
                observation[7],
                observation[8]
            ),
            observations
        ))

        if self.render_mode == "human":
            self.render(observations[0])

        if any(terminations):
            self.agents = []

        return map(
            lambda values: dict(zip(action_agents, values)),
            (
                observations,
                rewards,
                terminations,
                repeat(False, len(action_agents)),
                repeat({}, len(action_agents))
            )
        )

    @lru_cache(maxsize=None)
    def action_space(self, agent):
        return gymnasium.spaces.Tuple((
            gymnasium.spaces.Discrete(2),                                # 移動なら0、フェンス設置なら1
            gymnasium.spaces.Box(-1, 1, shape=[2], dtype=np.float32),    # 移動
            gymnasium.spaces.Tuple((                                     # フェンス設置
                gymnasium.spaces.Discrete(8),                            # row
                gymnasium.spaces.Discrete(8),                            # column
                gymnasium.spaces.Discrete(2)                             # 横なら0、縦なら1
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
            gymnasium.spaces.Discrete(11),                               # 敵の残りフェンス数
            gymnasium.spaces.Discrete(11),                               # 自分が次にフェンスを設置できるようになるまでの時間
            gymnasium.spaces.Discrete(11)                                # 敵が次にフェンスを設置できるようになるまでの時間
        ))
