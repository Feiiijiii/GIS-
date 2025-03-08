<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>用户注册</h2>
      <form @submit.prevent="register">
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
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email"
            v-model="email" 
            required 
            placeholder="请输入邮箱"
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
        <button type="submit" class="submit-btn">注册</button>
        <div class="auth-links">
          已有账号？ <router-link to="/login">立即登录</router-link>
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

const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()

const register = async () => {
  try {
    // 确保所有字段都有值
    if (!username.value || !email.value || !password.value) {
      errorMessage.value = '请填写所有必填字段';
      return;
    }
    
    // 添加基本的邮箱格式验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.value)) {
      errorMessage.value = '请输入有效的邮箱地址';
      return;
    }

    // 添加密码长度验证
    if (password.value.length < 6) {
      errorMessage.value = '密码长度至少为6个字符';
      return;
    }

    const response = await axios.post('http://localhost:8000/api/tourism/register/', {
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value
    });

    console.log('注册成功:', response.data);
    router.push('/login');
  } catch (error) {
    console.error('注册错误详情:', {
      data: error.response?.data,
      status: error.response?.status,
      message: error.response?.data?.message || error.message
    });
    
    // 处理后端返回的具体错误信息
    if (error.response?.data) {
      const data = error.response.data;
      if (Array.isArray(data.username)) {
        errorMessage.value = data.username[0];
      } else if (Array.isArray(data.email)) {
        errorMessage.value = data.email[0];
      } else if (Array.isArray(data.password)) {
        errorMessage.value = data.password[0];
      } else if (data.error) {
        errorMessage.value = data.error;
      } else if (data.detail) {
        errorMessage.value = data.detail;
      } else {
        errorMessage.value = '注册失败，请重试';
      }
    } else {
      errorMessage.value = '注册失败，请稍后重试';
    }
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
