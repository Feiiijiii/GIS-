<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>用户登录</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username"
            v-model="username" 
            required 
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password"
            v-model="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <button type="submit" class="submit-btn">登录</button>
        <div class="auth-links">
          还没有账号？ <router-link to="/register">立即注册</router-link>
        </div>
      </form>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useRoute } from 'vue-router'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()
const authStore = useAuthStore()
const route = useRoute()

const login = async () => {
  try {
    const response = await axios.post('http://localhost:8000/api/tourism/login/', {
      username: username.value,
      password: password.value,
    })
    console.log('登录成功:', response.data)
    
    // 存储token
    if (response.data.token) {
      localStorage.setItem('token', response.data.token)
    } else {
      // 如果后端没有返回token，我们创建一个临时的标识
      localStorage.setItem('token', 'temp_token_' + Date.now())
    }
    
    // 设置认证状态
    authStore.setAuth(true)
    authStore.setUser({ username: username.value })
    
    // 获取重定向路径（如果有）
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '登录失败，请重试'
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - var(--nav-height));
  background-color: var(--background-color);
  padding: 2rem;
}

.auth-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

h2 {
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.auth-links {
  text-align: center;
  margin-top: 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.auth-links a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-links a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #ef4444;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  text-align: center;
}
</style>
