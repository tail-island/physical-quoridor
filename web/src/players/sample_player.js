import { map, range, repeat } from 'ramda'

// 敵の観測結果を取得します。
function getEnemyObservation(observation) {
    const result = repeat(null, 9)

    result[0] = [-observation[2][0], -observation[2][1]]
    result[1] = [-observation[3][0], -observation[3][1]]
    result[2] = [-observation[0][0], -observation[0][1]]
    result[3] = [-observation[1][0], -observation[1][1]]

    result[4] = map(
        i => map(
            j => map(
                k => observation[4][7 - i][7 - j][k],
                range(0, 2)
            ),
            range(0, 8)
        ),
        range(0, 8)
    )

    result[5] = observation[6]
    result[6] = observation[5]
    result[7] = observation[8]
    result[8] = observation[7]

    return result
}
