import { append, map, range, repeat } from 'ramda'
import { PriorityQueue } from '@datastructures-js/priority-queue'

// 敵の観測結果を取得します。

function getEnemyObservation (observation) {
  const result = repeat(null, 9)

  result[0] = [-observation[2][0], -observation[2][1]]
  result[1] = [-observation[3][0], -observation[3][1]]
  result[2] = [-observation[0][0], -observation[0][1]]
  result[3] = [-observation[1][0], -observation[1][1]]
  result[4] = map(i => map(j => map(k => observation[4][7 - i][7 - j][k], range(0, 2)), range(0, 8)), range(0, 8))
  result[5] = observation[6]
  result[6] = observation[5]
  result[7] = observation[8]
  result[8] = observation[7]

  return result
}

// 最短経路を求めます。

function getShortestPath (observation) {
  const position = (() => {
    const [x, y] = observation[0]

    return [Math.round(-y + 4) * 2, Math.round(x + 4) * 2]
  })()

  const fences = (() => {
    const result = map(i => map(j => 0, range(0, 17)), range(0, 17))

    for (const r of range(0, 8)) {
      for (const c of range(0, 8)) {
        for (const isVertical of range(0, 2)) {
          if (!observation[4][r][c][isVertical]) {
            continue
          }

          for (const [deltaRow, deltaColumn] of isVertical === 0 ? [[1, 0], [1, 2]] : [[0, 1], [2, 1]]) {
            result[r * 2 + deltaRow][c * 2 + deltaColumn] = 1
          }
        }
      }
    }

    return result
  })()

  const priorityQueue = PriorityQueue.fromArray([[0, [position]]], (route1, route2) => Math.sign(route1[0] - route2[0]))
  const visiteds = new Set([position[0] * 17 + position[1]])

  while (!priorityQueue.isEmpty()) {
    const route = priorityQueue.dequeue()[1]

    const previousPosition = route[route.length - 1]

    if (previousPosition[1] === 16) {
      return map(position => [Math.floor(position[0] / 2), Math.floor(position[1] / 2)], route)
    }

    for (const nextPosition of map(delta => [previousPosition[0] + delta[0], previousPosition[1] + delta[1]], [[-2, 0], [0, 2], [2, 0], [0, -2]])) {
      if (visiteds.has(nextPosition[0] * 17 + nextPosition[1]) || !(nextPosition[0] >= 0 && nextPosition[0] < 17) || !(nextPosition[1] >= 0 && nextPosition[1] < 17) || fences[(previousPosition[0] + nextPosition[0]) / 2][(previousPosition[1] + nextPosition[1]) / 2]) {
        continue
      }

      const nextRoute = append(nextPosition, route)

      visiteds.add(nextPosition[0] * 17 + nextPosition[1])
      priorityQueue.enqueue([nextRoute.length * 2 + 16 - nextPosition[1], nextRoute])
    }
  }

  return null
}

function getShortestPathWithFence (observation, r, c, isVertical) {
  if (isVertical) {
    if (observation[4][r][c][0] || observation[4][r][c][1] || (r > 0 && observation[4][r - 1][c][1]) || (r < 7 && observation[4][r + 1][c][1])) {
      return null
    }
  } else {
    if (observation[4][r][c][1] || observation[4][r][c][0] || (c > 0 && observation[4][r][c - 1][0]) || (c < 7 && observation[4][r][c + 1][0])) {
      return null
    }
  }

  const originalFences = JSON.parse(JSON.stringify(observation[4]))

  observation[4][r][c][isVertical] = 1
  const shortestPath = getShortestPath(observation)

  observation[4] = originalFences

  return shortestPath
}

export class SamplePlayer {
  getFence (observation) {
    const enemyObservation = getEnemyObservation(observation)

    let maxDistance = getShortestPath(enemyObservation).length
    let fence = null

    for (const r of range(0, 8)) {
      for (const c of range(0, 8)) {
        for (const isVertical of range(0, 2)) {
          const shortestPath = getShortestPathWithFence(enemyObservation, r, c, isVertical)
          if (shortestPath === null) {
            continue
          }

          const distance = shortestPath.length
          if (distance > maxDistance) {
            fence = [7 - r, 7 - c, isVertical]
            maxDistance = distance
          }
        }
      }
    }

    return fence
  }

  getForce (observation) {
    const shortestPath = getShortestPath(observation)

    if (shortestPath.length === 1) {
      return [0.5, 0]
    }

    const [row, column] = shortestPath[1]

    const [positionX, positionY] = observation[0]
    const [velocityX, velocityY] = observation[1]

    return [column - 4 - positionX - velocityX, (row - 4) * -1 - positionY - velocityY]
  }

  getAction (observation) {
    if (observation[5] > 0 && observation[7] === 0) {
      const fence = this.getFence(observation)

      if (fence !== null) {
        return [1, [0, 0], fence]
      }
    }

    return [0, this.getForce(observation), [0, 0, 0]]
  }
}
