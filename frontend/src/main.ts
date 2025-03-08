import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
import axios from 'axios'

// 配置 axios 默认值
axios.defaults.baseURL = 'http://localhost:8000'//后端地址  
axios.defaults.headers.common['Content-Type'] = 'application/json'//请求头类型

// 添加请求拦截器，在请求头中添加token，如果token存在，则添加到请求头中，否则不添加
//token 是用户登录后返回的，用于验证用户身份
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

app.mount('#app')
