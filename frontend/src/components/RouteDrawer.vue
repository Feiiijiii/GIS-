<template>
  <div class="route-drawer" :class="{ 'is-open': isOpen }">
    <div class="drawer-header">
      <h3>路径规划</h3>
      <button class="close-btn" @click="close">×</button>
    </div>
    
    <div class="drawer-content">
      <div class="route-inputs">
        <!-- 起点选择 -->
        <div class="input-group">
          <label>起点</label>
          <select v-model="startPoint" @change="calculateRoute">
            <option value="">请选择起点</option>
            <option v-for="spot in spots" :key="spot.id" :value="spot">
              {{ spot.name }}
            </option>
          </select>
        </div>
        
        <!-- 终点选择 -->
        <div class="input-group">
          <label>终点</label>
          <select v-model="endPoint" @change="calculateRoute">
            <option value="">请选择终点</option>
            <option v-for="spot in spots" :key="spot.id" :value="spot">
              {{ spot.name }}
            </option>
          </select>
        </div>
        
        <!-- 交通方式选择 -->
        <div class="input-group">
          <label>交通方式</label>
          <div class="transport-options">
            <button 
              v-for="mode in transportModes" 
              :key="mode.value"
              :class="{ active: selectedMode === mode.value }"
              @click="selectMode(mode.value)"
            >
              {{ mode.icon }} {{ mode.label }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 路径详情 -->
      <div v-if="routeInfo" class="route-info">
        <div class="info-header">
          <h4>路线详情</h4>
          <span class="route-stats">
            {{ routeInfo.distance }}公里 · {{ routeInfo.duration }}分钟
          </span>
        </div>
        
        <div class="route-steps">
          <div v-for="(step, index) in routeInfo.steps" :key="index" class="step-item">
            <span class="step-icon">{{ step.icon }}</span>
            <div class="step-content">
              <p>{{ step.instruction }}</p>
              <small>{{ step.distance }}米</small>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <!-- 加载提示 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>正在规划路线...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { scenicSpotApi } from '../services/api'

// 声明 AMap 类型
declare const AMap: any

// 定义属性
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['update:isOpen', 'showRoute'])

// 状态变量
interface Spot {
  id: string;
  name: string;
  coordinates: [number, number];
}

const spots = ref<Spot[]>([])
const startPoint = ref<Spot | null>(null)
const endPoint = ref<Spot | null>(null)
const selectedMode = ref('driving')
const isLoading = ref(false)
const error = ref('')
const routeInfo = ref<any>(null)

// 交通方式选项
const transportModes = [
  { label: '驾车', value: 'driving', icon: '🚗' },
  { label: '步行', value: 'walking', icon: '🚶' },
  { label: '公交', value: 'transit', icon: '🚌' }
]

// 添加类型定义
interface TransitPlan {
  segments: Array<{
    instruction?: string;
    walking_distance?: number;
    distance?: number;
    transit_mode?: string;
    path?: number[][];
  }>;
  distance: number;
  time: number;
}

interface DrivingRoute {
  distance: number;
  time: number;
  steps: Array<{
    instruction: string;
    distance: number;
    path: number[][];
  }>;
}

interface TransitResult {
  status: string;
  info: string;
  plans: TransitPlan[];
}

interface DrivingResult {
  status: string;
  info: string;
  routes: DrivingRoute[];
}

// 加载景点数据
const loadSpots = async () => {
  try {
    const response = await scenicSpotApi.getGeoJson()
    if (response.data && response.data.features) {
      spots.value = response.data.features.map((feature: any) => ({
        id: feature.properties.id || Math.random().toString(),
        name: feature.properties.name,
        coordinates: feature.geometry.coordinates
      }))
    }
  } catch (error) {
    console.error('加载景点数据失败:', error)
  }
}

// 选择交通方式
const selectMode = (mode: string) => {
  selectedMode.value = mode
  if (startPoint.value && endPoint.value) {
    calculateRoute()
  }
}

// 添加插件加载检查函数
const checkPluginLoaded = (pluginName: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (AMap[pluginName]) {
      resolve()
      return
    }

    AMap.plugin([`AMap.${pluginName}`], () => {
      if (AMap[pluginName]) {
        resolve()
      } else {
        reject(new Error(`${pluginName} 插件加载失败`))
      }
    })
  })
}

// 添加API初始化验证
const validateAMapAPI = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    let retryCount = 0;
    const maxRetries = 5;
    
    const checkAPI = () => {
      if (typeof AMap === 'undefined') {
        if (retryCount >= maxRetries) {
          reject(new Error('高德地图API加载超时'));
          return;
        }
        retryCount++;
        setTimeout(checkAPI, 500);
        return;
      }

      // 验证安全配置
      if (!window._AMapSecurityConfig?.securityJsCode) {
        reject(new Error('高德地图安全配置未正确设置'));
        return;
      }

      // 验证必要插件
      const requiredPlugins = ['Driving', 'Walking', 'Transfer'];
      const missingPlugins = requiredPlugins.filter(plugin => !AMap[plugin]);

      if (missingPlugins.length > 0) {
        console.log('尝试加载缺失插件:', missingPlugins);
        // 尝试加载缺失的插件
        AMap.plugin(missingPlugins.map(p => `AMap.${p}`), () => {
          const stillMissing = requiredPlugins.filter(plugin => !AMap[plugin]);
          if (stillMissing.length > 0) {
            reject(new Error(`以下插件未正确加载: ${stillMissing.join(', ')}`));
          } else {
            console.log('API验证成功:', {
              plugins: requiredPlugins.map(plugin => `${plugin}: ${!!AMap[plugin]}`),
              securityConfig: window._AMapSecurityConfig?.securityJsCode
            });
            resolve();
          }
        });
      } else {
        console.log('API验证成功:', {
          plugins: requiredPlugins.map(plugin => `${plugin}: ${!!AMap[plugin]}`),
          securityConfig: window._AMapSecurityConfig?.securityJsCode
        });
        resolve();
      }
    };

    checkAPI();
  });
};

// 计算路线
const calculateRoute = async () => {
  if (!startPoint.value || !endPoint.value) return
  
  isLoading.value = true
  error.value = ''
  
  try {
    // 检查坐标是否有效
    const isValidCoord = (coord: number[]) => {
      return coord && coord.length === 2 && 
             coord[0] >= 103.5 && coord[0] <= 104.5 && // 成都经度范围
             coord[1] >= 30.4 && coord[1] <= 31.0      // 成都纬度范围
    }

    if (!isValidCoord(startPoint.value.coordinates) || !isValidCoord(endPoint.value.coordinates)) {
      throw new Error('起点或终点坐标超出成都市范围')
    }

    const origin = `${startPoint.value.coordinates[0]},${startPoint.value.coordinates[1]}`
    const destination = `${endPoint.value.coordinates[0]},${endPoint.value.coordinates[1]}`
    
    console.log('开始路径规划:', {
      mode: selectedMode.value,
      origin,
      destination
    })

    // 构建API请求URL
    const baseUrl = '/amap/v3/direction'
    const params = new URLSearchParams({
      key: '1e85723b6a7dabf095a0ef6b230741cf',  // 更新为新的Web服务API key
      origin,
      destination,
      output: 'json',
      city: '成都',
      extensions: 'all'
    })

    // 根据不同交通方式调用不同接口
    let url = ''
    if (selectedMode.value === 'driving') {
      url = `${baseUrl}/driving?${params}&strategy=0`
    } else if (selectedMode.value === 'walking') {
      url = `${baseUrl}/walking?${params}`
    } else if (selectedMode.value === 'transit') {
      url = `${baseUrl}/transit/integrated?${params}&city1=成都&city2=成都`
    }

    console.log('请求URL:', url)

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    const data = await response.json()

    console.log('路径规划返回结果:', data)

    if (data.status === '1') {
      if (selectedMode.value === 'transit') {
        const route = data.route.transits[0]
        routeInfo.value = {
          distance: (route.distance / 1000).toFixed(1),
          duration: Math.ceil(route.duration / 60),
          steps: route.segments.map((segment: any) => ({
            instruction: segment.instruction || '步行至下一站',
            distance: segment.walking_distance || segment.distance || 0,
            icon: segment.transit_mode === 'WALK' ? '🚶' : '🚌'
          }))
        }

        // 处理路线坐标点
        const path = route.segments.flatMap((segment: any) => {
          let points: number[][] = []
          
          // 处理步行段
          if (segment.walking && segment.walking.steps) {
            points = points.concat(
              segment.walking.steps.flatMap((step: any) => 
                step.polyline ? step.polyline.split(';').map((point: string) => {
                  const [lng, lat] = point.split(',').map(Number)
                  return [lng, lat]
                }) : []
              )
            )
          }
          
          // 处理公交段
          if (segment.bus && segment.bus.buslines && segment.bus.buslines[0]) {
            points = points.concat(
              segment.bus.buslines[0].polyline.split(';').map((point: string) => {
                const [lng, lat] = point.split(',').map(Number)
                return [lng, lat]
              })
            )
          }
          
          return points
        })

        console.log('公交路线数据:', {
          path,
          pathLength: path.length,
          firstPoint: path[0],
          lastPoint: path[path.length - 1],
          startPoint: startPoint.value.coordinates,
          endPoint: endPoint.value.coordinates
        })

        // 发送路线数据到父组件
        console.log('RouteDrawer - 准备发送路线数据')
        const routeData = {
          path,
          info: routeInfo.value,
          type: selectedMode.value,
          startPoint: startPoint.value.coordinates,
          endPoint: endPoint.value.coordinates
        }
        console.log('RouteDrawer - 发送的数据:', routeData)
        emit('showRoute', routeData)
      } else {
        const route = data.route.paths[0]
        routeInfo.value = {
          distance: (route.distance / 1000).toFixed(1),
          duration: Math.ceil(route.duration / 60),
          steps: route.steps.map((step: any) => ({
            instruction: step.instruction,
            distance: step.distance,
            icon: getStepIcon(selectedMode.value)
          }))
        }

        // 处理路线坐标点
        const path = route.steps.flatMap((step: any) => 
          step.polyline ? step.polyline.split(';').map((point: string) => {
            const [lng, lat] = point.split(',').map(Number)
            return [lng, lat]  // 返回坐标数组
          }) : []
        )

        console.log('驾车/步行路线数据:', {
          path,
          pathLength: path.length,
          firstPoint: path[0],
          lastPoint: path[path.length - 1],
          startPoint: startPoint.value.coordinates,
          endPoint: endPoint.value.coordinates
        })

        // 发送路线数据到父组件
        console.log('RouteDrawer - 准备发送路线数据')
        const routeData = {
          path,
          info: routeInfo.value,
          type: selectedMode.value,
          startPoint: startPoint.value.coordinates,
          endPoint: endPoint.value.coordinates
        }
        console.log('RouteDrawer - 发送的数据:', routeData)
        emit('showRoute', routeData)
      }
    } else {
      throw new Error(data.info || '路线规划失败')
    }
  } catch (err: any) {
    console.error('路径规划错误:', err)
    
    // 根据错误类型显示不同的错误信息
    if (err.message.includes('INVALID_USER_SCODE')) {
      error.value = '服务授权验证失败，请检查密钥配置'
    } else if (err.message.includes('DAILY_QUERY_OVER_LIMIT')) {
      error.value = '当日服务调用次数已达上限'
    } else if (err.message.includes('NETWORK_ERROR')) {
      error.value = '网络连接失败，请检查网络设置'
    } else if (err.message.includes('未找到合适的路线')) {
      error.value = '抱歉，未找到合适的路线，请尝试其他交通方式'
    } else {
      error.value = '路线规划失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

// 获取步骤图标
const getStepIcon = (mode: string) => {
  switch (mode) {
    case 'driving':
      return '🚗'
    case 'walking':
      return '🚶'
    case 'transit':
      return '🚌'
    default:
      return '➡️'
  }
}

// 关闭抽屉
const close = () => {
  emit('update:isOpen', false)
}

// 监听打开状态
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadSpots()
  } else {
    // 清空状态
    startPoint.value = null
    endPoint.value = null
    routeInfo.value = null
    error.value = ''
  }
})
</script>

<style scoped>
.route-drawer {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.route-drawer.is-open {
  right: 0;
}

.drawer-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--primary-color);
  color: white;
}

.drawer-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: transform 0.2s ease;
}

.close-btn:hover {
  transform: scale(1.1);
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.route-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-weight: 500;
  color: var(--text-secondary);
}

.input-group select {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  background: white;
}

.transport-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.transport-options button {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.transport-options button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.route-info {
  background: var(--background-color);
  border-radius: var(--radius-lg);
  padding: 1rem;
  margin-top: 1rem;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.info-header h4 {
  margin: 0;
  color: var(--text-primary);
}

.route-stats {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.route-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.step-icon {
  font-size: 1.2rem;
}

.step-content {
  flex: 1;
}

.step-content p {
  margin: 0;
  color: var(--text-primary);
}

.step-content small {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.error-message {
  color: #ef4444;
  background: #fee2e2;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  margin-top: 1rem;
  text-align: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 