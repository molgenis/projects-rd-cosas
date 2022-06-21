import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import CosasDashboard from './pages/CosasDashboard.vue'
import VariantDBSearchUI from './pages/VariantDbSearchUI.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/cosas-dashboard', component: CosasDashboard },
  { path: '/variantdb-search', component: VariantDBSearchUI }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
