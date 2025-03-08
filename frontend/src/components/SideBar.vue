<template>
  <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed }">
    <div class="sidebar-header">
      <h2>功能面板</h2>
      <button class="collapse-btn" @click="toggleCollapse" :title="isCollapsed ? '展开' : '收起'">
        {{ isCollapsed ? '›' : '‹' }}
      </button>
    </div>
    <div class="sidebar-content">
      <div class="search-box">
        <input 
          type="text" 
          placeholder="点击搜索景点..." 
          v-model="searchQuery"
          :class="{ 'is-searching': isSearching }"
        />
        <div class="search-spinner" v-if="isSearching"></div>
      </div>
      
      <!-- 搜索结果 -->
      <div class="search-results" v-if="searchQuery.trim() && searchResults.length > 0">
        <h3>搜索结果</h3>
        <div class="results-list">
          <div 
            class="spot-card" 
            v-for="spot in searchResults" 
            :key="spot.id" 
            @click="selectSpot(spot)"
          >
            <div class="spot-info">
              <h4>{{ spot.name }}</h4>
              <p>{{ spot.shortDesc }}</p>
              <span class="spot-category">{{ spot.category }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 搜索错误提示 -->
      <div class="search-error" v-if="searchError">
        {{ searchError }}
      </div>
      
      <!-- 无搜索结果提示 -->
      <div class="no-results" v-if="searchQuery.trim() && searchResults.length === 0 && !isSearching && !searchError">
        未找到相关景点
      </div>
      
      <!-- 功能菜单 -->
      <div class="sidebar-section" v-if="!searchQuery.trim() || searchResults.length === 0">
        <h3>功能选择</h3>
        <button 
          class="sidebar-item" 
          v-for="(item, index) in menuItems" 
          :key="index" 
          :class="{ 'active': item.action === 'area' && isDrawingArea }"
          @click="handleItemClick(item)"
        >
          <span class="item-icon">{{ item.icon }}</span>
          <span class="item-label">{{ item.label }}</span>
        </button>
      </div>
      
      <!-- 区域选择结果 -->
      <div class="sidebar-section" v-if="isDrawingArea || selectedAreaSpots.length > 0">
        <div class="section-header">
          <h3>区域选择</h3>
          <div class="section-actions">
            <button 
              v-if="showViewSpotsButton" 
              class="view-btn" 
              @click="viewAreaSpots"
            >
              查看景点
            </button>
            <button 
              class="clear-btn" 
              @click="clearAreaSelection"
            >
              清除
            </button>
          </div>
        </div>
        <div v-if="isDrawingArea" class="drawing-tip">
          请在地图上绘制区域...
        </div>
        <div v-else-if="selectedAreaSpots.length > 0" class="selected-spots">
          <div class="spots-count">
            已选择 {{ selectedAreaSpots.length }} 个景点
          </div>
        </div>
      </div>
      
      <!-- 热门景点 -->
      <div class="sidebar-section" v-if="!searchQuery.trim()">
        <h3>热门景点</h3>
        <div class="popular-spots">
          <div class="spot-card" v-for="(spot, index) in popularSpots" :key="index" @click="selectSpot(spot)">
            <div class="spot-image" :style="{ backgroundImage: `url(${spot.imageUrl || '/placeholder.jpg'})` }"></div>
            <div class="spot-info">
              <h4>{{ spot.name }}</h4>
              <p>{{ spot.shortDesc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { scenicSpotApi } from '../services/api'
import type { Route } from '../types/route'

// 添加防抖函数
function debounce<T extends (...args: any[]) => any>(fn: T, delay: number) {
  let timeoutId: NodeJS.Timeout
  return function (...args: Parameters<T>) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(null, args), delay)
  }
}

const isCollapsed = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const isSearching = ref(false)
const searchError = ref('')

const menuItems = [
  { label: '区域选择', action: 'area', icon: '⭕' },
  { label: '路线规划', action: 'route', icon: '🗺️' },
  { label: '收藏景点', action: 'favorites', icon: '⭐' },
  { label: '图层控制', action: 'layers', icon: '📊' }
]

const popularSpots = [
  { 
    name: '宽窄巷子', 
    shortDesc: '成都著名的历史文化街区',
    imageUrl: 'https://img95.699pic.com/photo/50061/9620.jpg_wh860.jpg'
  },
  { 
    name: '锦里古街', 
    shortDesc: '三国文化主题商业步行街',
    imageUrl: 'https://fxpai.com/wp-content/uploads/2020/11/fd08806b64ee0ba9aa082d0c1bf9ae8c.jpg'
  },
  { 
    name: '都江堰', 
    shortDesc: '世界文化遗产，古代水利工程',
    imageUrl: 'https://img1.qunarzz.com/travel/poi/201407/30/cc58461b40f01e3cc8d65eac.jpg'
  }
]

// 添加区域选择状态   
const isDrawingArea = ref(false)
const selectedAreaSpots = ref<any[]>([])
const showViewSpotsButton = ref(false)

// 添加当前活动功能状态
const currentAction = ref('')

// 使用防抖包装搜索函数
const debouncedSearch = debounce(async (query: string) => {
  if (query.trim().length > 1) {
    await searchSpots(query)
  } else {
    searchResults.value = []
  }
}, 300)

// 监听搜索输入
watch(searchQuery, (newValue) => {
  debouncedSearch(newValue)
})

// 搜索景点
const searchSpots = async (query: string) => {
  if (!query.trim()) return
  
  isSearching.value = true
  searchError.value = ''
  searchResults.value = []
  
  try {
    const response = await scenicSpotApi.search(query)
    console.log('搜索响应:', response.data)
    
    if (response.data && response.data.type === 'FeatureCollection' && response.data.features) {
      const features = response.data.features
      console.log('搜索结果:', features)
      
      if (!features || features.length === 0) {
        searchError.value = `未找到与"${query}"相关的景点`
        return
      }
      
      searchResults.value = features.map((feature: any) => {
        if (!feature || !feature.properties) {
          console.error('发现无效的景点数据:', feature)
          return null
        }
        
        try {
          const properties = feature.properties
          // 处理描述文本，确保不为空
          let description = properties.description || ''
          if (description.length > 150) {
            description = description.substring(0, 150) + '...'
          } else if (!description) {
            description = '暂无描述'
          }
          
          return {
            id: properties.id || Math.random().toString(),
            name: properties.name || '未知景点',
            shortDesc: description,
            category: properties.category || '未分类',
            coordinates: feature.geometry?.coordinates || [104.07, 30.67],
            address: properties.address || '成都市',
            openTime: properties.opening_hours || '暂无信息',
            price: properties.ticket_price ? `¥${properties.ticket_price}` : '免费',
            imageUrl: (properties.images && properties.images.length > 0)
              ? properties.images[0]
              : '/placeholder.jpg'
          }
        } catch (err) {
          console.error('处理景点数据时出错:', err, feature)
          return null
        }
      }).filter(Boolean)

      if (searchResults.value.length === 0) {
        searchError.value = `未找到与"${query}"相关的有效景点数据`
        return
      }

      // 如果只有一个搜索结果，自动选中并显示
      if (searchResults.value.length === 1) {
        selectSpot(searchResults.value[0])
      }
    } else {
      console.error('API响应格式不符合预期:', response.data)
      searchError.value = '搜索结果格式无效，请稍后重试'
    }
  } catch (error: any) {
    console.error('搜索景点时出错:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 404:
          searchError.value = `未找到与"${query}"相关的景点`
          break
        case 500:
          searchError.value = '服务器暂时无法响应，请稍后重试'
          break
        case 503:
          searchError.value = '服务器正在维护，请稍后重试'
          break
        default:
          searchError.value = error.response.data?.message || '搜索失败，请稍后重试'
      }
    } else if (error.request) {
      searchError.value = '无法连接到服务器，请检查网络连接'
    } else {
      searchError.value = '搜索失败，请稍后重试'
    }

    // 5秒后自动清除错误提示
    setTimeout(() => {
      if (searchError.value) {
        searchError.value = ''
      }
    }, 5000)
  } finally {
    isSearching.value = false
  }
}
// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
// 发送事件
// 定义一个函数，用于发送事件到父组件
// 该函数接受一个参数，表示要发送的事件名称
const emit = defineEmits(['spotSelected', 'startDrawArea', 'stopDrawArea', 'clearArea', 'showAreaSpots', 'showSearchSpot', 'showRoute', 'openRouteDrawer'])

// 处理菜单项点击
// 定义一个函数，用于处理菜单项的点击事件
// 该函数接受一个参数，表示被点击的菜单项
// 该函数会根据菜单项的 action 属性执行相应的操作
const handleItemClick = (item: { label: string, action: string, icon: string }) => {
  console.log(`Selected: ${item.label}`)
  currentAction.value = item.action
  
  if (item.action === 'area') {
    if (!isDrawingArea.value) {
      isDrawingArea.value = true
      emit('startDrawArea')
    } else {
      isDrawingArea.value = false
      emit('stopDrawArea')
    }
  } else if (item.action === 'route') {
    // 添加调试日志
    console.log('路径规划按钮被点击')
    console.log('触发 openRouteDrawer 事件')
    emit('openRouteDrawer')
  }
}

// 处理区域选择结果
const handleAreaSelected = (spots: any[]) => {
  selectedAreaSpots.value = spots
  isDrawingArea.value = false
  
  // 如果有选中的景点，显示查看按钮
  if (spots.length > 0) {
    showViewSpotsButton.value = true
  }
}

// 清除区域选择
const clearAreaSelection = () => {
  selectedAreaSpots.value = []
  emit('clearArea')
}

// 查看区域内景点
const viewAreaSpots = () => {
  showViewSpotsButton.value = false
  // 发送事件通知父组件显示景点
  emit('showAreaSpots')
  // 发送选中的景点信息
  selectedAreaSpots.value.forEach(spot => {
    emit('spotSelected', {
      name: spot.getTitle(),
      description: '区域内景点',
      address: '成都市',
      openTime: '暂无信息',
      price: '暂无信息',
      imageUrl: null,
      coordinates: [spot.getPosition().getLng(), spot.getPosition().getLat()]
    })
  })
}

defineExpose({
  handleAreaSelected
})
// 选中景点
const selectSpot = (spot: any) => {
  console.log(`Selected spot: ${spot.name}`)
  // 发送选中的景点信息
  emit('spotSelected', {
    name: spot.name,
    description: spot.shortDesc || spot.description,
    address: spot.address || '成都市',
    openTime: spot.openTime || spot.opening_hours || '暂无信息',
    price: spot.price || spot.ticket_price || '免费',
    imageUrl: spot.imageUrl,
    coordinates: spot.coordinates
  })
  // 触发显示单个景点
  emit('showSearchSpot', spot.coordinates)
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100%;
  background: var(--card-bg);
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.08);
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  border-right: 1px solid var(--border-color);
  z-index: 50;
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  background-color: #4CAF50;
  color: white;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  color: white;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.sidebar-content {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
  scrollbar-width: thin;
  scrollbar-color: var(--text-light) transparent;
}

.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background-color: var(--text-light);
  border-radius: 6px;
}

.search-box {
  margin-bottom: 1.5rem;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  background-color: var(--card-bg);
  color: var(--text-primary);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.search-box input.is-searching {
  background-color: rgba(59, 130, 246, 0.05);
}

.search-box::before {
  content: '🔍';
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
  font-size: 1rem;
  pointer-events: none;
}

.search-spinner {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: translateY(-50%) rotate(360deg); }
}

.search-box input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}

.search-results h3,
.sidebar-section h3 {
  margin-bottom: 1rem;
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.5rem;
}

.search-results h3::after,
.sidebar-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background: var(--primary-color);
  border-radius: 2px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem;
}

.search-error {
  color: #ef4444;
  background-color: #fee2e2;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
}

.no-results {
  color: var(--text-secondary);
  background-color: var(--background-color);
  padding: 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
}

.sidebar-section {
  margin-bottom: 1.5rem;
}

.sidebar-item {
  width: 100%;
  padding: 0.85rem 1.25rem;
  margin-bottom: 0.75rem;
  background: var(--background-color);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  color: var(--text-primary);
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.item-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.item-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: var(--primary-color);
  transform: scaleY(0);
  transition: transform var(--transition-fast);
}

.sidebar-item:hover {
  background: var(--card-bg);
  color: var(--primary-color);
  transform: translateX(5px);
  box-shadow: var(--shadow-md);
}

.sidebar-item:hover::before {
  transform: scaleY(1);
}

.popular-spots {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.spot-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease;
  min-height: 140px;
  height: auto;
  border: 1px solid var(--border-color);
  position: relative;
  padding: 1rem;
  will-change: transform;
}

.spot-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.spot-image {
  width: 100%;
  min-height: 180px;
  height: 100%;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  position: relative;
}

.spot-image::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.1));
}

.spot-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: 100%;
}

.spot-info h4 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.4;
}

.spot-info p {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  flex: 1;
}

.spot-category {
  display: inline-block;
  font-size: 0.85rem;
  background-color: var(--primary-color);
  color: white;
  padding: 0.35rem 1rem;
  border-radius: 1rem;
  margin-top: auto;
  max-width: fit-content;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.sidebar-collapsed .sidebar-header h2,
.sidebar-collapsed .search-box,
.sidebar-collapsed .sidebar-section h3,
.sidebar-collapsed .item-label,
.sidebar-collapsed .popular-spots,
.sidebar-collapsed .search-results {
  display: none;
}

.sidebar-collapsed .sidebar-item {
  padding: 0.85rem;
  justify-content: center;
}

.sidebar-collapsed .item-icon {
  margin: 0;
}

@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
  }

  .sidebar.active {
    transform: translateX(0);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.clear-btn {
  padding: 4px 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.clear-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
  background: var(--background-color);
}

.selected-spots {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selected-spots .spot-card {
  padding: 0.75rem;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.selected-spots .spot-card:hover {
  transform: translateX(5px);
  border-color: var(--primary-color);
  background: var(--background-color);
}

.selected-spots h4 {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.sidebar-item.active {
  background: var(--primary-color);
  color: white;
}

.sidebar-item.active:hover {
  background: var(--primary-dark);
}

.section-actions {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 4px 8px;
  font-size: 0.875rem;
  color: white;
  background: var(--primary-color);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: transform 0.2s ease;
  will-change: transform;
}

.view-btn:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
}

.drawing-tip {
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: center;
  padding: 1rem;
  background: var(--background-color);
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
}

.spots-count {
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  text-align: center;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

/* 优化其他元素的过渡效果 */
.sidebar-item {
  transition: transform 0.2s ease;
  will-change: transform;
}

.collapse-btn {
  transition: transform 0.2s ease;
  will-change: transform;
}
</style>
