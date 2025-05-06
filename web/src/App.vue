<script setup>
import ActionsLog from './components/ActionsLog.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import GameBoard from '@/components/GameBoard.vue'
</script>

<template>
  <main>
    <div class="game">
      <GameBoard class="game-item" />
      <ActionsLog class="game-item" />
    </div>
    <ControlPanel />
  </main>
</template>

<style>
body {
  font-family: Arial;
  font-size: 14px;
}

.game {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}
</style>
