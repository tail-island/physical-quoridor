<script setup>
import { range } from 'ramda'
import { onMounted, watch } from 'vue'
import { usePhysicalQuoridorStore } from '@/stores/PhysicalQuoridorStore'

const store = usePhysicalQuoridorStore()

onMounted(() => {
  watch(() => store.observations, observations => {
    const context = document.getElementById('canvas').getContext('2d')

    context.fillStyle = '#000'

    context.fillRect(0, 0, 450, 450)

    context.strokeStyle = '#888'

    for (const i of range(1, 8 + 1)) {
      context.beginPath()
      context.moveTo(i * 50, 0)
      context.lineTo(i * 50, 450)
      context.closePath()
      context.stroke()
    }

    for (const i of range(1, 8 + 1)) {
      context.beginPath()
      context.moveTo(0, i * 50)
      context.lineTo(450, i * 50)
      context.closePath()
      context.stroke()
    }

    context.fillStyle = '#fff'

    for (const row of range(0, 8)) {
      for (const column of range(0, 8)) {
        for (const direction of range(0, 2)) {
          if (!observations[0][4][row][column][direction]) {
            continue
          }

          if (direction === 0) {
            context.fillRect(column * 50 - 5, (row + 1) * 50 - 5, 110, 10)
          } else {
            context.fillRect((column + 1) * 50 - 5, row * 50 - 5, 10, 110)
          }
        }
      }
    }

    context.fillStyle = '#f88'

    context.beginPath()
    context.arc((observations[0][0][0] + 4.5) * 50, (-observations[0][0][1] + 4.5) * 50, 10, 0, Math.PI * 2)
    context.closePath()
    context.fill()

    context.fillStyle = '#88f'

    context.beginPath()
    context.arc((observations[0][2][0] + 4.5) * 50, (-observations[0][2][1] + 4.5) * 50, 10, 0, Math.PI * 2)
    context.closePath()
    context.fill()
  })
})
</script>

<template>
<div>
  <canvas id="canvas" width="450" height="450"></canvas>
</div>
</template>
