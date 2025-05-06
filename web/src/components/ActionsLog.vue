<script setup>
import { onMounted } from 'vue'
import { usePhysicalQuoridorStore } from '@/stores/PhysicalQuoridorStore'

const store = usePhysicalQuoridorStore()

onMounted(() => {
  const observer = new MutationObserver((mutations, observer) => {
    for (const mutation of mutations) {
      mutation.target.lastElementChild?.scrollIntoView(false)
    }
  })

  observer.observe(document.getElementById('actions-log'), { childList: true })
})
</script>

<template>
<div id="actions-log" class="actions-log">
  <div v-for="(actions, index) in store.actionsLog" :key="index" class="actions">
    {{ actions[0] }}
    <br>
    {{ actions[1] }}
  </div>
</div>
</template>

<style scoped>
.actions-log {
  border: 1px solid #808080;
  font-size: 12px;
  height: 450px;
  margin-left: 10px;
  width: 390px;
  overflow-y: scroll;
}

.actions {
  margin: 8px 8px;
}
</style>
