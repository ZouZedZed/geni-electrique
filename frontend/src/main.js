import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import { createRouter, createWebHistory } from 'vue-router'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

import App from './App.vue'
import SearchView from './views/SearchView.vue'
import CatalogueView from './views/CatalogueView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: SearchView,    name: 'search' },
    { path: '/catalogue', component: CatalogueView, name: 'catalogue' },
  ]
})

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'dark',
  },
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(vuetify)
  .mount('#app')
