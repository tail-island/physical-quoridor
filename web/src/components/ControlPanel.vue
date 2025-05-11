<script setup>
import { any } from 'ramda'
import { onMounted } from 'vue'
import { usePhysicalQuoridorStore } from '@/stores/PhysicalQuoridorStore'

const store = usePhysicalQuoridorStore()

function newGame () {
  store.newGame(document.getElementById('enemy-name').value)
}

function step () {
  const actionItems = [
    parseInt(document.getElementById('action-type').value),
    parseFloat(document.getElementById('force-x').value),
    parseFloat(document.getElementById('force-y').value),
    parseInt(document.getElementById('row').value),
    parseInt(document.getElementById('column').value),
    parseInt(document.getElementById('direction').value)
  ]

  if (any(actionItem => isNaN(actionItem), actionItems)) {
    alert('入力値が不正です。')
    return
  }

  store.step([actionItems[0], [actionItems[1], actionItems[2]], [actionItems[3], actionItems[4], actionItems[5]]])
}

onMounted(() => {
  newGame()
})
</script>

<template>
  <p>
    <select id="enemy-name">
      <option value="doNothingPlayer">DoNothingPlayer</option>,
      <option value="randomPlayer">RandomPlayer</option>,
      <option value="samplePlayer" selected>SamplePlayer</option>
    </select>
    &nbsp;
    <button id="new-game-button" @click="newGame">New Game</button>
  </p>
  <p>
    [
    <input id="action-type" size="1" value="0">
    ,&nbsp;[
    <input id="force-x" size="5" value="0.5">
    ,&nbsp;
    <input id="force-y" size="5" value="0.0">
    ],&nbsp;[
    <input id="row" size="1" value="0">
    ,&nbsp;
    <input id="column" size="1" value="0">
    ,&nbsp;
    <input id="direction" size="1" value="0">
    ]]
    <button id="step-button" @click="step" :disabled="!store.terminations || store.terminations[0]">Step</button>
  </p>
  <div v-if="store.observations">
    <p>
      位置 = ({{ store.observations[0][0][0] }}, {{ store.observations[0][0][1] }}), 速度 = ({{ store.observations[0][1][0] }}, {{ store.observations[0][1][1] }}), 残りフェンス数 = {{ store.observations[0][5] }}, フェンス設置になるまでのステップ数 = {{ store.observations[0][7] }}
      <br>
      位置 = ({{ store.observations[0][2][0] }}, {{ store.observations[0][2][1] }}), 速度 = ({{ store.observations[0][3][0] }}, {{ store.observations[0][3][1] }}), 残りフェンス数 = {{ store.observations[0][6] }}, フェンス設置になるまでのステップ数 = {{ store.observations[0][8] }}
    </p>
  </div>
</template>
