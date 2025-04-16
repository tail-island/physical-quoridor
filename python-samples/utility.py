import numpy as np

from heapq import heappop, heappush


# 最短経路を求めます。
def get_shortest_path(observation):
    # セルの間まで含めた、17×17のマップを使用して、A*アルゴリズムで最短の経路を求めます。

    # 17×17のマップの中での、現在位置を取得します。
    def get_position():
        x, y = observation[0]

        return int(round(-y + 4) * 2), int(round(x + 4) * 2)  # y座標と行は向きが異なるので符号反転し、原点の位置が異なるので調整しています。また、セルの間に壁があるので、2倍しておきます。

    # 17×17のマップの中での、フェンスの設置状況を取得します。
    def get_fences():
        result = np.zeros((17, 17), dtype=np.int8)

        for row, column, is_vertical in zip(*np.where(observation[4])):
            for delta_row, delta_column in [[0, 1], [2, 1]] if is_vertical else [[1, 0], [1, 2]]:
                result[row * 2 + delta_row, column * 2 + delta_column] = 1

        return result

    # 現在位置とマップを取得します。
    position = get_position()
    fences = get_fences()

    # A*アルゴリズムに必要な、プライオリティ・キュー（Pythonではheqpqを使用するのでリスト）と探索済みの位置を保存するセットを作成します。
    heap = [(0, (position,))]
    visiteds = {position}

    # 経路候補が残っている間はループします。
    while heap:
        # 最も損失が少ない経路候補を取得します。
        _, route = heappop(heap)

        # 経路の最後の位置を取得します。
        position = route[-1]

        # ゴールしたなら（右端のセルに辿り着いたら）……
        if position[1] == 16:
            # セルの間を含まない形で経路をリターンします。
            return list(map(lambda position: (position[0] // 2, position[1] // 2), route))

        # 次の位置でループします。
        for next_position in map(lambda delta: (position[0] + delta[0], position[1] + delta[1]), [[-2, 0], [0, 2], [2, 0], [0, -2]]):  # セルの間の壁の分を考慮して、2セル進みます。
            # 訪問済みか、ボードの範囲外か、移動途中にフェンスがある場合は……
            if next_position in visiteds or not (0 <= next_position[0] < 17 and 0 <= next_position[1] < 17) or fences[(position[0] + next_position[0]) // 2, (position[1] + next_position[1]) // 2]:
                # コンティニューして、次の位置へ進む経路は破棄します。
                continue

            # 次の経路を作成します。
            next_route = route + (next_position,)

            # 探索済みとしてマークし、経路をプライオリティ・キューに追加します。
            visiteds.add(next_position)
            heappush(heap, (len(next_route[1:]) * 2 + 16 - next_position[1], next_route))  # A*なので、これまでの歩数＋これからの歩数の予測の最小値もキューに追加します。セルの間の壁の分を考慮して、これまでの距離は2倍します。

    # ゴールできる経路が見つからなかった場合はNoneをリターンします。
    return None  # ゴールできないようなフェンス設置はルールで禁止されているので、必ずゴールできる経路があるはず。なので、Noneを返してもエラーにならないはず。
