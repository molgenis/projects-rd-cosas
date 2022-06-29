import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import Cosas from './pages/HomePageCosas.vue'
import CosasDashboard from './pages/CosasDashboard.vue'
import Ucu from './pages/HomePageUnsolvedCases.vue'
import VariantDb from './pages/HomePageVariantDb.vue'

const routes = [
  {
    name: 'home',
    path: '/',
    component: Home
  },
  {
    name: 'cosas',
    path: '/cosas',
    component: Cosas
  },
  {
    name: 'cosasdashboard',
    path: '/cosas-dashboard',
    component: CosasDashboard
  },
  {
    name: 'ucu',
    path: '/unsolvedcases',
    component: Ucu
  },
  {
    name: 'variantdb',
    path: '/variantdb',
    component: VariantDb
  }
]

const router = createRouter({
  history: createWebHistory(window.location.pathname),
  routes,
  scrollBehavior (to, from, savedPosition) {
    return {
      top: 0
    }
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
