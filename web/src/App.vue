<script setup>
import ActionsLog from './components/ActionsLog.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import GameBoard from '@/components/GameBoard.vue'
</script>

<template>
  <main>
    <div>
      <GameBoard />
      <ControlPanel />
      <ActionsLog />
    </div>
  </main>
</template>

<style>
body {
  font-family: Arial;
  font-size: 14px;
}
</style>
