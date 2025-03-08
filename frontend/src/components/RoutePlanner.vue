<template>
  <div class="route-planner">
    <!-- 偏好选择部分 -->
    <div class="preferences-section" v-if="!showRoutes">
      <h3>选择您的游玩偏好</h3>
      
      <!-- 游玩天数选择 -->
      <div class="days-selector">
        <label>计划游玩天数</label>
        <div class="days-options">
          <button 
            v-for="day in [1,2,3,4,5]" 
            :key="day"
            :class="{ active: selectedDays === day }"
            @click="selectedDays = day"
          >
            {{ day }}天
          </button>
        </div>
      </div>

      <!-- 偏好标签选择 -->
      <div class="preferences-tags">
        <label>选择游玩偏好（可多选）</label>
        <div class="tags-container">
          <button
            v-for="(tag, index) in preferenceTags"
            :key="index"
            :class="{ active: selectedTags.includes(tag.value) }"
            @click="toggleTag(tag.value)"
          >
            {{ tag.icon }} {{ tag.label }}
          </button>
        </div>
      </div>

      <!-- 其他偏好选项 -->
      <div class="additional-preferences">
        <div class="preference-item">
          <label>预算范围</label>
          <select v-model="budget">
            <option value="low">经济实惠 (¥0-500)</option>
            <option value="medium">中等消费 (¥500-1000)</option>
            <option value="high">高端享受 (¥1000+)</option>
          </select>
        </div>

        <div class="preference-item">
          <label>交通方式</label>
          <select v-model="transportation">
            <option value="public">公共交通</option>
            <option value="car">自驾游</option>
            <option value="walk">步行为主</option>
          </select>
        </div>
      </div>

      <!-- 生成路线按钮 -->
      <button 
        class="generate-btn"
        @click="generateRoutes"
        :disabled="!canGenerateRoutes"
      >
        生成推荐路线
      </button>
    </div>

    <!-- 路线展示部分 -->
    <div class="routes-section" v-else>
      <div class="routes-header">
        <h3>为您推荐的路线</h3>
        <button class="back-btn" @click="showRoutes = false">
          重新选择偏好
        </button>
      </div>

      <div class="routes-container">
        <div 
          v-for="(route, index) in recommendedRoutes" 
          :key="index"
          class="route-card"
          :class="{ active: selectedRouteIndex === index }"
          @click="selectRoute(index)"
        >
          <div class="route-header">
            <h4>路线 {{ index + 1 }}</h4>
            <span class="route-stats">
              {{ route.duration }} | 预计花费: ¥{{ route.estimatedCost }}
            </span>
          </div>
          
          <div class="route-spots">
            <div 
              v-for="(spot, spotIndex) in route.spots" 
              :key="spotIndex" 
              class="route-spot"
            >
              <div class="spot-time">{{ spot.suggestedTime }}</div>
              <div class="spot-content">
                <h5>{{ spot.name }}</h5>
                <p>{{ spot.description }}</p>
                <div class="spot-tags">
                  <span v-for="tag in spot.tags" :key="tag">{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="route-footer">
            <button class="view-on-map-btn" @click.stop="viewRouteOnMap(route)">
              在地图上查看
            </button>
            <button class="share-btn" @click.stop="shareRoute(route)">
              分享路线
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 过滤景点展示部分 -->
    <div v-if="showFilteredSpots" class="filtered-spots-section">
      <h3>符合条件的景点 ({{ filteredSpots.length }}个)</h3>
      <div class="filtered-spots-grid">
        <div v-for="spot in filteredSpots" :key="spot.id" class="spot-card">
          <h4>{{ spot.name }}</h4>
          <div class="spot-price">门票: ¥{{ spot.ticket_price || '免费' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Route, RoutePreferences, Spot } from '../types/route'
import { scenicSpotApi } from '../services/api'
import axios from 'axios'

// 用户偏好选项
const preferenceTags = [
  { label: '历史文化', value: 'history', icon: '🏛️' },
  { label: '美食探索', value: 'food', icon: '🍜' },
  { label: '自然风光', value: 'nature', icon: '🌳' },
  { label: '购物娱乐', value: 'shopping', icon: '🛍️' },
  { label: '艺术展馆', value: 'art', icon: '🎨' },
  { label: '古镇民俗', value: 'folk', icon: '🏮' },
  { label: '主题乐园', value: 'theme', icon: '🎡' },
  { label: '休闲度假', value: 'leisure', icon: '☕' }
]

// 状态管理
const selectedDays = ref(1)
const selectedTags = ref<string[]>([])
const budget = ref('medium')
const transportation = ref('public')
const showRoutes = ref(false)
const selectedRouteIndex = ref(-1)
const recommendedRoutes = ref<Route[]>([])
const filteredSpots = ref<Spot[]>([])
const showFilteredSpots = ref(false)

// 计算属性
const canGenerateRoutes = computed(() => {
  return selectedTags.value.length > 0
})

// 方法
const toggleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}
// 生成路线
const generateRoutes = async () => {
  try {
    const preferences: RoutePreferences = {
      days: selectedDays.value,
      preferences: selectedTags.value,
      budget: budget.value as 'low' | 'medium' | 'high',
      transportation: transportation.value as 'public' | 'car' | 'walk'
    }

    // 1. 获取符合用户偏好的景点
    const spotsResponse = await scenicSpotApi.filter(preferences)
    filteredSpots.value = spotsResponse.data
    showFilteredSpots.value = true

    // 2. 使用高德地图API规划路线
    const routes: Route[] = []
    const spots_per_day = 3
    const total_days = preferences.days

    // 将景点按天数分组
    for (let day = 0; day < total_days; day++) {
      const daySpots = spotsResponse.data.slice(day * spots_per_day, (day + 1) * spots_per_day)
      if (daySpots.length < 2) continue

      try {
        // 构建途经点
        const waypoints = daySpots.slice(1, -1).map((spot: Spot) => 
          `${spot.longitude},${spot.latitude}`
        ).join(';')

        // 根据交通方式选择不同的路径规划API
        const routeType = preferences.transportation === 'walk' ? 'walking' : 'driving'
        
        // 调用高德路径规划API
        const amapResponse = await axios.get(`https://restapi.amap.com/v3/direction/${routeType}`, {
          params: {
            key: import.meta.env.VITE_AMAP_KEY,
            origin: `${daySpots[0].longitude},${daySpots[0].latitude}`,
            destination: `${daySpots[daySpots.length - 1].longitude},${daySpots[daySpots.length - 1].latitude}`,
            waypoints: waypoints,
            strategy: preferences.transportation === 'car' ? 10 : 0, // 10:考虑实时路况
            output: 'json'
          }
        })

        if (amapResponse.data.status === '1') {
          const route = amapResponse.data.route
          const newRoute: Route = {
            id: `day-${day + 1}`,
            name: `第${day + 1}天行程`,
            description: `包含${daySpots.length}个景点的行程`,
            duration: formatDuration(Number(route.paths[0].duration)),
            estimatedCost: calculateCost(daySpots),
            transportation: preferences.transportation,
            distance: formatDistance(Number(route.paths[0].distance)),
            difficulty: calculateDifficulty(route.paths[0].distance, daySpots.length),
            spots: daySpots.map((spot: Spot, index: number) => ({
              ...spot,
              order: index + 1,
              suggestedTime: formatTime(9 + index * 3),
              stayDuration: 120
            })),
            path: route.paths[0].steps.map((step: any) => ({
              instruction: step.instruction,
              distance: step.distance,
              duration: step.duration,
              polyline: step.polyline
            }))
          }
          routes.push(newRoute)
        }
      } catch (error) {
        console.error(`规划第${day + 1}天路线时出错:`, error)
      }
    }

    recommendedRoutes.value = routes
    showRoutes.value = true
    
    // 如果生成了路线，自动显示第一条路线
    if (routes.length > 0) {
      selectRoute(0)
      emit('showRoute', routes[0])
    }
  } catch (error: any) {
    console.error('生成路线失败:', error)
    const errorMessage = error.response?.data?.message || error.message || '获取推荐路线失败'
    alert(errorMessage)
  }
}

// 辅助函数
// 格式化时间
const formatTime = (hour: number): string => {
  const h = hour % 24
  return `${h.toString().padStart(2, '0')}:00`
}
// 格式化时长
const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
}
// 格式化距离
const formatDistance = (meters: number): string => {
  return meters >= 1000 ? `${(meters / 1000).toFixed(1)}公里` : `${meters}米`
}
// 计算费用
const calculateCost = (spots: Spot[]): number => {
  return spots.reduce((total, spot) => {
    return total + (Number(spot.ticket_price) || 0)
  }, 0)
}
// 计算难度
const calculateDifficulty = (distance: number, spotCount: number): 'easy' | 'moderate' | 'hard' => {
  const totalDistance = Number(distance)
  if (totalDistance > 20000 || spotCount > 4) return 'hard'
  if (totalDistance > 10000 || spotCount > 3) return 'moderate'
  return 'easy'
}
// 选择路线
const selectRoute = (index: number) => {
  selectedRouteIndex.value = index
  if (index >= 0 && index < recommendedRoutes.value.length) {
    emit('showRoute', recommendedRoutes.value[index])
  }
}
// 在地图上查看路线
const viewRouteOnMap = (route: Route) => {
  emit('showRoute', route)
}
// 分享路线 
const shareRoute = (route: Route) => {
  // TODO: 实现路线分享功能
}

// 定义事件
const emit = defineEmits<{
  (e: 'showRoute', route: Route): void
}>()
</script>

<style scoped>
.route-planner {
  padding: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.preferences-section,
.routes-section {
  max-width: 800px;
  margin: 0 auto;
}

h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.days-selector,
.preferences-tags,
.additional-preferences {
  margin-bottom: 2rem;
}

label {
  display: block;
  margin-bottom: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.days-options {
  display: flex;
  gap: 0.5rem;
}

.days-options button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.days-options button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.tags-container button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.tags-container button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.additional-preferences {
  display: grid;
  gap: 1rem;
}

.preference-item select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.generate-btn:disabled {
  background: var(--border-color);
  cursor: not-allowed;
}

.routes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.routes-container {
  display: grid;
  gap: 1.5rem;
}

.route-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.route-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.route-card.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.route-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.route-stats {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.route-spots {
  display: grid;
  gap: 1rem;
}

.route-spot {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: var(--radius-md);
}

.spot-time {
  font-size: 0.9rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.spot-content h5 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.spot-content p {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.spot-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.spot-tags span {
  padding: 0.25rem 0.5rem;
  background: var(--primary-color-light);
  color: var(--primary-color);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
}

.route-footer {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

.view-on-map-btn,
.share-btn {
  flex: 1;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-on-map-btn {
  background: var(--primary-color);
  color: white;
  border: none;
}

.share-btn {
  background: var(--background-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.view-on-map-btn:hover {
  background: var(--primary-dark);
}

.share-btn:hover {
  background: var(--card-bg);
  border-color: var(--primary-color);
}

.filtered-spots-section {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

.filtered-spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.spot-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1rem;
}

.spot-card h4 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.spot-price {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
</style> 