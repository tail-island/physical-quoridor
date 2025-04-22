import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())

app.mount('#app')

import { PhysicalQuoridor } from 'physical-quoridor'

const physical_quoridor = new PhysicalQuoridor(BigInt(1234))
console.log(physical_quoridor.step([
    [1, [2.0, 3.0], [4, 5, 6]],
    [1, [2.0, 3.0], [4, 5, 6]]
]))
