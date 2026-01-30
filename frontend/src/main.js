import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './styles/main.css'
import { setupGlobalFetchInterceptor } from './utils/api'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')

// グローバルfetchで429をハンドリング
setupGlobalFetchInterceptor()
