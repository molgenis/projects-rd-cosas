import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Cosas from '@/pages/HomePageCosas.vue'
import CosasDashboard from '@/pages/CosasDashboard.vue'
import VariantDb from '@/pages/HomePageVariantDb.vue'
import Help from '@/pages/Help.vue'

const initialState = window.__INITIAL_STATE__ || {}

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
    name: 'variantdb',
    path: '/variantdb',
    component: VariantDb
  },
  {
    name: 'help',
    path: '/help',
    component: Help
  }
]

const router = createRouter({
  history: createWebHistory(initialState.baseUrl),
  routes,
  scrollBehavior (to, from, savedPosition) {
    return {
      top: 0
    }
  }
})

export default router
