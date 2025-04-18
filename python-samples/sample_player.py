import numpy as np
import sys

from funcy import partial
from player import Player
from utility import get_enemy_observation, get_shortest_path, get_shortest_path_with_fence


class SamplePlayer(Player):
    def __init__(self, seed=None):
        # ログはfile=sys.stderrをつけて出力します。ログは、gameディレクトリのplayer-x.logに出力されます。
        print("*** SamplePlayer ***", file=sys.stderr)

    @classmethod
    def _get_fence(cls, observation):
        # 敵の気分になるために、敵の観測結果を取得します。
        enemy_observation = get_enemy_observation(observation)

        # 最短経路が最も長くなるフェンスの設置位置を取得します。
        max_distance = len(get_shortest_path(enemy_observation))
        fence = None

        # まだフェンスが設置されていない全ての設置位置で、最も最短距離が長い設置位置を取得します。
        for row, column, is_vertical in map(partial(map, int), zip(*np.where(np.array(enemy_observation[4]) == 0))):
            # 指定した位置にフェンスを設置した場合の最短経路を取得します。
            shortest_path = get_shortest_path_with_fence(enemy_observation, row, column, is_vertical)
            if shortest_path is None:
                continue

            # これまでで最も長い最短経路よりも長い経路だったら……
            distance = len(shortest_path)
            if distance > max_distance:
                # 設置位置を更新します。
                fence = 7 - row, 7 - column, is_vertical
                max_distance = distance

        # 設置位置をリターンします。fenceには最初にNoneを代入したので、フェンスを設置しても最短経路が長くならない場合はNoneがリターンされます。
        return fence

    @classmethod
    def _get_force(cls, observation):
        # 最短経路を取得します。
        shortest_path = get_shortest_path(observation)

        # ゴールラインのセルにいるなら……
        if len(shortest_path) == 1:
            # まっすぐゴールに進みます。
            return [1, 0]

        # 次に進むべきセルを取得します。
        row, column = shortest_path[1]

        # 観測結果から、位置と速度を取得します。
        position_x, position_y = observation[0]
        velocity_x, velocity_y = observation[1]

        # 座標系の違いに配慮しながら、次のセルに向かう力をリターンします。
        return [column - 4 - position_x - velocity_x, (row - 4) * -1 - position_y - velocity_y]

    def get_action(self, observation):
        # フェンスを設置可能なら……
        if observation[5] > 0 and observation[7] == 0:
            # 敵の最短経路がもっと長くなるフェンスの設置位置を取得します。
            fence = self._get_fence(observation)

            # 敵の最短経路が長くなるフェンスの設置位置があるなら……
            if fence is not None:
                # フェンスを設置します。
                return 1, [0, 0], fence

        # 最短経路を進むように、駒に力を加えます。
        return 0, self._get_force(observation), (0, 0, 0)


if __name__ == "__main__":
    SamplePlayer().run()
