/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 13:42:29
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-13 23:20:42
 */
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/css/tailwind.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'

library.add(fas)


const app = createApp(App)


app.use(router)


app.mount('#app')

