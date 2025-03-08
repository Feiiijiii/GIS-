import { defineStore } from 'pinia'

interface User {
  username: string
}

interface AuthState {
  isAuthenticated: boolean
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => {
    // 从localStorage中恢复状态
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    return {
      isAuthenticated: !!token,
      user: savedUser ? JSON.parse(savedUser) : null
    }
  },

  actions: {
    setAuth(status: boolean) {
      this.isAuthenticated = status
      if (!status) {
        localStorage.removeItem('token')
      }
    },

    setUser(user: User) {
      this.user = user
      // 保存用户信息到localStorage
      localStorage.setItem('user', JSON.stringify(user))
    },

    logout() {
      // 清除认证状态
      this.isAuthenticated = false
      this.user = null
      
      // 清除本地存储的token和其他用户相关数据
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 如果有其他用户相关的数据也需要清除
      // 例如：收藏的景点等
      localStorage.removeItem('favorites')
      
      // 清除可能存在的session storage数据
      sessionStorage.clear()
    },

    // 初始化认证状态
    initAuth() {
      const token = localStorage.getItem('token')
      const savedUser = localStorage.getItem('user')
      
      if (token && savedUser) {
        this.isAuthenticated = true
        this.user = JSON.parse(savedUser)
      }
    }
  }
}) 