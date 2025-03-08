<template>
  <!-- 应用程序主容器 -->
  <div class="app">
    <!-- 已登录用户界面：包含导航栏和主要内容 -->
    <template v-if="authStore.isAuthenticated">
      <!-- 导航栏组件：处理地图类型切换和图层控制 -->
      <NavBar 
        @map-type-change="handleMapTypeChange"
        @layer-toggle="handleLayerToggle" />
      
      <!-- 路由视图：动态加载不同页面组件 -->
      <router-view 
        :mapType="currentMapType" 
        :activeLayers="activeLayers"
        v-slot="{ Component }">
        <component 
          :is="Component" 
          :mapType="currentMapType"
          :activeLayers="activeLayers" />
      </router-view>
      
      <!-- API测试功能区：用于开发调试 -->
      <button class="api-test-toggle" @click="showApiTest = !showApiTest">
        {{ showApiTest ? '隐藏API测试' : '显示API测试' }}
      </button>
      <div v-if="showApiTest" class="api-test-overlay">
        <ApiTest />
      </div>
    </template>

    <!-- 未登录用户界面：显示登录/注册页面 -->
    <template v-else>
      <router-view></router-view>
    </template>
  </div>
</template>

<script setup lang="ts">
// 导入必要的组件和功能
import { ref, onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import ApiTest from './components/ApiTest.vue'
import { useAuthStore } from './stores/auth'

// 状态管理
const showApiTest = ref(false)          // 控制API测试面板的显示状态
const currentMapType = ref('default')    // 当前地图类型
const activeLayers = ref<string[]>([])   // 激活的地图图层列表
const authStore = useAuthStore()         // 认证状态管理

// 组件初始化
onMounted(() => {
  authStore.initAuth()  // 初始化认证状态
})

// 地图类型切换处理函数
const handleMapTypeChange = (mapType: string) => {
  console.log('地图类型变更为:', mapType)
  currentMapType.value = mapType
}

// 图层显示控制处理函数
const handleLayerToggle = ({ layer, visible }: { layer: string, visible: boolean }) => {
  console.log('图层切换:', layer, visible ? '显示' : '隐藏')
  if (visible && !activeLayers.value.includes(layer)) {
    activeLayers.value.push(layer)
  } else if (!visible) {
    activeLayers.value = activeLayers.value.filter(l => l !== layer)
  }
}
</script>

<style>
:root {
  --nav-height: 4rem;
  --sidebar-width: 280px;
  --info-sidebar-width: 350px;
  
  /* 颜色方案 */
  --primary-color: #3b82f6;
  --primary-dark: #2563eb;
  --primary-light: #60a5fa;
  --secondary-color: #10b981;
  --accent-color: #f59e0b;
  --background-color: #f8fafc;
  --card-bg: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-light: #94a3b8;
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  
  /* 圆角 */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  
  /* 动画 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--background-color);
  color: var(--text-primary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.app {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  height: calc(100% - var(--nav-height));
  overflow: hidden;
  width: 100%;
  background-color: var(--background-color);
}

.map-container {
  flex: 1;
  position: relative;
  min-width: 0;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.api-test-toggle {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-fast);
}

.api-test-toggle:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.api-test-overlay {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 400px;
  max-height: 500px;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  overflow: auto;
  padding: 20px;
}

button {
  cursor: pointer;
  font-family: inherit;
  border: none;
  background: none;
  transition: all var(--transition-fast);
}

input, select, textarea {
  font-family: inherit;
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--card-bg);
  color: var(--text-primary);
  transition: all var(--transition-fast);
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

@media (max-width: 768px) {
  .main-container {
    position: relative;
  }
}
</style>
