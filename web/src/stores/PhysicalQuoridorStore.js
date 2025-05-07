import { PhysicalQuoridor } from 'physical-quoridor'
import { defineStore } from 'pinia'
import { append, map, range, repeat } from 'ramda'
import { ref } from 'vue'
import { RandomPlayer } from '@/players/RandomPlayer'
import { SamplePlayer } from '@/players/SamplePlayer'

const initialObservation = [[-4.0, 0.0], [0.0, 0.0], [4.0, 0.0], [0.0, 0.0], map(i => map(j => map(k => 0, range(0, 2)), range(0, 8)), range(0, 8)), 10, 10, 0, 0]

const enemies = {
  randomPlayer: new RandomPlayer(),
  samplePlayer: new SamplePlayer()
}

export const usePhysicalQuoridorStore = defineStore('gameState', () => {
  let physicalQuoridor = null
  let enemy = null

  const observations = ref(null)
  const rewards = ref(null)
  const terminations = ref(null)
  const actionsLog = ref(null)

  function newGame (enemyName) {
    physicalQuoridor = new PhysicalQuoridor(BigInt(Math.floor(Math.random() * 1_000) + 1))
    enemy = enemies[enemyName]

    observations.value = repeat(initialObservation, 2)
    rewards.value = [0.0, 0.0]
    terminations.value = [false, false]

    actionsLog.value = []
  }

  function step (action) {
    const actions = [
      action,
      enemy.getAction(observations.value[1])
    ]

    actionsLog.value = append(actions, actionsLog.value ?? [])

    const [nextObservations, nextRewards, nextTerminations] = physicalQuoridor.step(actions)

    observations.value = nextObservations
    rewards.value = nextRewards
    terminations.value = nextTerminations
  }

  return { observations, rewards, terminations, actionsLog, newGame, step }
})
