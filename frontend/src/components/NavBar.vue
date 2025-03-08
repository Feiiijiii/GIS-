<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <img src="../assets/travel.png" alt="Logo" class="logo" />
      <h1 class="title">成都市旅游服务系统</h1>
    </div>
    <div class="navbar-menu" :class="{ show: isMobileMenuOpen }">
      <button v-for="(item, index) in menuItems" :key="index" 
        :class="['menu-item', { active: currentRoute === item.route }]" 
        @click="handleMenuItemClick(item)">
        {{ item.label }}
        <span v-if="item.hasDropdown" class="dropdown-arrow" 
          :class="{ 'dropdown-arrow-active': showDropdown === item.route }">▼</span>
        <div v-if="item.hasDropdown && showDropdown === item.route" 
          class="dropdown-menu">
          <div v-for="(category, idx) in item.dropdownItems" :key="idx" class="dropdown-category">
            <div class="category-title">{{ category.title }}</div>
            <button v-for="(subItem, subIdx) in category.items" 
              :key="subIdx"
              class="dropdown-item"
              @click.stop="handleSubNavigation(subItem.route)">
              {{ subItem.label }}
            </button>
          </div>
        </div>
      </button>
      <div class="map-type-selector">
        <button class="map-type-btn" :class="{ active: currentMapType === 'default' }"
          @click="changeMapType('default')">
          标准地图
        </button>
        <button class="map-type-btn" :class="{ active: currentMapType === 'satellite' }"
          @click="changeMapType('satellite')">
          卫星地图
        </button>
      </div>
      <button class="mobile-menu-btn" @click="toggleMobileMenu">
        <span class="menu-icon">☰</span>
      </button>
    </div>
    <div class="nav-right">
      <div class="weather-info">
        <span class="weather-item">
          <i class="weather-icon">🌤️</i>
          <span>{{ weather.temperature }}°C</span>
        </span>
        <span class="weather-item">
          <i class="weather-icon">💨</i>
          <span>AQI: {{ weather.aqi }}</span>
        </span>
      </div>
      <span class="username">{{ authStore.user?.username }}</span>
      <button class="logout-btn" @click="handleLogout">登出</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 路由和认证状态管理
const router = useRouter()
const authStore = useAuthStore()

// 导航状态管理
const currentRoute = ref('home')         // 当前路由
const currentMapType = ref('default')    // 当前地图类型
const isMobileMenuOpen = ref(false)      // 移动端菜单状态
const showDropdown = ref('')             // 当前展开的下拉菜单

// 导航菜单配置
const menuItems = [
  { label: '首页', route: 'home' },
  { label: '景点详情', route: 'spots-detail' },
  { 
    label: '旅游服务', 
    route: 'routes',
    hasDropdown: true,
    dropdownItems: [
      {
        title: '酒店住宿',
        items: [
          { label: '酒店', route: 'hotels' },
          { label: '民宿', route: 'homestays' }
        ]
      },
      {
        title: '公共交通',
        items: [
          { label: '公交站', route: 'bus-stops' },
          { label: '地铁站', route: 'metro-stations' },
          { label: '停车场', route: 'parking-lots' }
        ]
      },
      {
        title: '餐饮服务',
        items: [
          { label: '川菜', route: 'sichuan-food' },
          { label: '火锅', route: 'hotpot' },
          { label: '小吃', route: 'snacks' },
          { label: '西餐', route: 'western-food' }
        ]
      }
    ]
  },
  { label: '关于', route: 'about' }
]

// 定义组件事件
const emit = defineEmits(['map-type-change', 'layer-toggle'])

// 导航处理函数
const handleNavigation = (route: string) => {
  currentRoute.value = route
  const menuItem = menuItems.find(item => item.route === route)
  if (menuItem?.hasDropdown) {
    return
  }
  router.push(route === 'home' ? '/' : `/${route}`)
}

// 地图类型切换处理
const changeMapType = (type: string) => {
  currentMapType.value = type
  emit('map-type-change', type)
}

// 移动端菜单切换
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
  showDropdown.value = ''
}

// 登出处理
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 天气信息管理
const weather = ref({
  temperature: '--',
  aqi: '--'
})

// 天气API配置
const WEATHER_CONFIG = {
  key: 'a648f1d5eb9c4021a9adaae061c8fdfa',
  location: '101270101', // 成都
  refreshInterval: 30 * 60 * 1000, // 30分钟
  endpoints: {
    weather: 'https://devapi.qweather.com/v7/weather/now',
    air: 'https://devapi.qweather.com/v7/air/now'
  }
}

// 天气数据获取函数
const fetchWeatherData = async () => {
  try {
    const [weatherResponse, airResponse] = await Promise.all([
      fetch(`${WEATHER_CONFIG.endpoints.weather}?location=${WEATHER_CONFIG.location}&key=${WEATHER_CONFIG.key}`),
      fetch(`${WEATHER_CONFIG.endpoints.air}?location=${WEATHER_CONFIG.location}&key=${WEATHER_CONFIG.key}`)
    ])

    if (!weatherResponse.ok || !airResponse.ok) {
      throw new Error('天气API请求失败')
    }

    const [weatherData, airData] = await Promise.all([
      weatherResponse.json(),
      airResponse.json()
    ])

    if (weatherData.code !== '200' || airData.code !== '200') {
      throw new Error('天气API返回错误')
    }

    weather.value = {
      temperature: weatherData.now.temp,
      aqi: airData.now.aqi,
    }
  } catch (error) {
    console.error('获取天气数据失败:', error)
    // 保持现有数据不变，避免显示出错
  }
}

// 图层映射配置
const layerMapping: Record<string, string> = {
  'hotels': 'ne:hotels',
  'homestays': 'ne:homestays',
  'bus-stops': 'ne:bus_stops',
  'metro-stations': 'ne:metro_stations',
  'parking-lots': 'ne:parking_lots',
  'sichuan-food': 'ne:sichuan_food',
  'hotpot': 'ne:hotpot',
  'snacks': 'ne:snacks',
  'western-food': 'ne:western_food'
} as const

// 子导航处理函数
const handleSubNavigation = (route: string) => {
  const layerName = layerMapping[route]
  if (layerName) {
    emit('layer-toggle', {
      layer: layerName,
      visible: true
    })
  }
  
  router.push(`/${route}`)
  showDropdown.value = ''
  isMobileMenuOpen.value = false
}

// 菜单项点击处理
const handleMenuItemClick = (item: any) => {
  if (item.hasDropdown) {
    showDropdown.value = showDropdown.value === item.route ? '' : item.route
  } else {
    handleNavigation(item.route)
    showDropdown.value = ''
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 初始获取天气数据
  fetchWeatherData()
  // 设置定时刷新
  setInterval(fetchWeatherData, WEATHER_CONFIG.refreshInterval)

  // 点击外部关闭下拉菜单
  document.addEventListener('click', (event: Event) => {
    const target = event.target as HTMLElement
    if (!target.closest('.menu-item') && !target.closest('.dropdown-menu')) {
      showDropdown.value = ''
    }
  })
})
</script>

<style scoped>
.navbar {
  height: var(--nav-height);
  background: linear-gradient(35deg, #2f721e, var(--primary-color));
  color: rgb(252, 247, 247);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  box-shadow: var(--shadow-md);
  position: relative;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 2.5rem;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  transition: transform var(--transition-fast);
}

.logo:hover {
  transform: scale(1.05);
}

.title {
  font-size: 2.0rem;
  font-weight: 600;
  font-family: '毛泽东体', 'STXingkai', '华文行楷', cursive;
  color: white;
  margin: 0;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.navbar-menu {
  display: flex;
  gap: 1rem;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
}

.menu-item {
  position: relative;
  overflow: visible;  /* 修改这里，允许下拉菜单显示 */
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.9);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.menu-item:hover,
.menu-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  transform: translateY(-2px);
}

.menu-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: white;
  transition: all var(--transition-normal);
  transform: translateX(-50%);
}

.menu-item:hover::after,
.menu-item.active::after {
  width: 80%;
}

.map-type-selector {
  display: flex;
  margin-left: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  padding: 0.25rem;
}

.map-type-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.9);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.map-type-btn.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.map-type-btn:hover {
  color: white;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: var(--text-primary);
  font-weight: 500;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: var(--background-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background-color: #fee2e2;
  border-color: #ef4444;
  color: #ef4444;
}

.weather-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: 2rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
}

.weather-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  font-size: 0.9rem;
}

.weather-icon {
  font-size: 1.2rem;
}

.dropdown-arrow {
  font-size: 0.8em;
  margin-left: 4px;
  transition: transform 0.3s ease;
}

.dropdown-arrow-active {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 250px;
  z-index: 1000;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
  opacity: 1;
  visibility: visible;
  transition: all 0.3s ease;
}

.dropdown-category {
  padding: 0.8rem;
  border-bottom: 1px solid var(--border-color);
}

.dropdown-category:last-child {
  border-bottom: none;
}

.category-title {
  color: var(--primary-color);
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.5rem;
  border: none;
  background: none;
  color: var(--text-primary);
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.dropdown-item:hover {
  background: var(--background-hover);
  color: var(--primary-color);
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.mobile-menu-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }

  .title {
    font-size: 1.2rem;
  }

  .menu-item,
  .map-type-selector,
  .weather-info {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .navbar-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    padding: 1rem;
    box-shadow: var(--shadow-md);
    flex-direction: column;
    align-items: stretch;
    display: none;
    z-index: 1000;  /* 确保菜单在最上层 */
  }

  .navbar-menu.show {
    display: flex;
  }

  .menu-item {
    display: block;
    color: var(--text-primary);
    text-align: left;
    width: 100%;
    padding: 0.8rem 1rem;  /* 增加点击区域 */
  }

  .dropdown-menu {
    position: static;
    transform: none;
    box-shadow: none;
    border: 1px solid var(--border-color);
    margin: 0.5rem 0;
    width: 100%;
    padding: 0;
  }

  .dropdown-category {
    padding: 0.5rem;
  }

  .dropdown-item {
    padding: 0.8rem 1rem;
  }
}
</style>
