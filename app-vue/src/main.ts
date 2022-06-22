import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

import App from './App.vue'
import Home from './pages/Home.vue'
import Cosas from './pages/HomePageCosas.vue'
import CosasDashboard from './pages/CosasDashboard.vue'
import Ucu from './pages/HomePageUnsolvedCases.vue'
import VariantDb from './pages/HomePageVariantDb.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/cosas', component: Cosas },
  { path: '/cosas-dashboard', component: CosasDashboard },
  { path: '/unsolvedcases', component: Ucu },
  { path: '/variantdb', component: VariantDb }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
