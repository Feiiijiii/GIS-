<template>
  <div class="map-container">
    <div id="map" class="map"></div>
    <RouteDrawer 
      v-model:isOpen="isDrawerOpen"
      @showRoute="handleShowRoute"
      ref="routeDrawer"
    />
    <div class="map-controls">
      <button class="control-btn" @click="centerToChengdu">
        <span>返回成都</span>
      </button>
      <button class="control-btn" @click="toggle3D">
        <span>{{ is3D ? '2D视图' : '3D视图' }}</span>
      </button>
      <button class="control-btn refresh-btn" @click="loadScenicSpots" :disabled="isLoading">
        <span>刷新景点</span>
      </button>
    </div>
    
    <!-- 加载指示器 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <p>加载景点数据...</p>
    </div>
    
    <!-- 错误提示 -->
    <div class="error-message" v-if="loadError">
      {{ loadError }}
      <button @click="loadScenicSpots">重试</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { scenicSpotApi } from '../services/api'
import RouteDrawer from './RouteDrawer.vue'

// 地图配置常量
const MAP_CONFIG = {
  CHENGDU: {
    lat: Number(import.meta.env.VITE_MAP_DEFAULT_LAT || 30.67),//成都的纬度
    lng: Number(import.meta.env.VITE_MAP_DEFAULT_LNG || 104.07),//成都的经度
    zoom: Number(import.meta.env.VITE_MAP_DEFAULT_ZOOM || 12)//成都的缩放级别
  },
  ICON: {
    BASE_SIZE: 24,      // 基础大小为24
    MIN_SIZE: 16,       // 最小大小为16
    MAX_SIZE: 32,       // 最大大小为32
    SCALE_FACTOR: 1.2,  // 保持缩放系数不变
    URL: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_bs.png'
  },
  VIEW_3D: {
    ROTATION: 30,
    PITCH: 45
  }
}

// 声明高德地图类型
declare const AMap: any
declare global {
  interface Window {
    _AMapSecurityConfig: {
      securityJsCode: string
    }
  }
}

// 组件属性定义
const props = defineProps({
  mapType: {
    type: String,
    default: 'default'
  },
  showSpots: {
    type: Boolean,
    default: false
  },
  activeLayers: {
    type: Array as () => string[],
    default: () => []
  }
})

// 地图状态管理
const map = ref<any>(null)                    // 地图实例
const mouseTool = ref<any>(null)              // 鼠标工具实例
const drawingPolygon = ref<any>(null)         // 绘制的多边形实例
const spots = ref<any[]>([])                  // 景点标记数组
const isLoading = ref(false)                  // 加载状态
const loadError = ref('')                     // 错误信息
const is3D = ref(false)                       // 3D视图状态
const wmsLayers = ref<Record<string, any>>({}) // WMS图层记录
const currentRoute = ref<any>(null)           // 当前路线
const routePolyline = ref<any>(null)          // 路线折线实例
const startMarker = ref<any>(null)            // 起点标记
const endMarker = ref<any>(null)              // 终点标记
const isDrawerOpen = ref(false)               // 抽屉状态
const routeDrawer = ref<any>(null)            // 路线抽屉实例

// 组件事件
const emit = defineEmits(['spotClick', 'areaSelected', 'updateMapType'])

// 监听地图类型变化
watch(() => props.mapType, (newType) => {
  if (!map.value) return
  
  const layers = []
  if (newType === 'satellite') {
    layers.push(
      new AMap.TileLayer.Satellite()
    )
  } else {
    layers.push(
      new AMap.TileLayer()
    )
  }
  map.value.setLayers(layers)
})

// 3D视图切换
const toggle3D = () => {
  if (!map.value) return
  is3D.value = !is3D.value
  
  if (is3D.value) {
    map.value.setRotation(MAP_CONFIG.VIEW_3D.ROTATION)
    map.value.setPitch(MAP_CONFIG.VIEW_3D.PITCH)
    map.value.setViewMode?.('3D')
  } else {
    map.value.setRotation(0)
    map.value.setPitch(0)
    map.value.setViewMode?.('2D')
  }
}

// 地图居中到成都
const centerToChengdu = () => {
  map.value?.setZoomAndCenter(
    MAP_CONFIG.CHENGDU.zoom,
    [MAP_CONFIG.CHENGDU.lng, MAP_CONFIG.CHENGDU.lat]
  )
}

// 清除地图标记
const clearMarkers = () => {
  spots.value.forEach(spot => spot.remove())
  spots.value = []
}

// 计算标记图标大小
const calculateIconSize = (zoom: number) => {
  // 使用对数计算来使缩放更平滑
  const baseZoom = MAP_CONFIG.CHENGDU.zoom
  const scaleFactor = MAP_CONFIG.ICON.SCALE_FACTOR
  const size = MAP_CONFIG.ICON.BASE_SIZE * Math.pow(scaleFactor, (zoom - baseZoom))
  
  return Math.min(
    Math.max(size, MAP_CONFIG.ICON.MIN_SIZE),
    MAP_CONFIG.ICON.MAX_SIZE
  )
}

// 创建景点标记
const createSpotMarker = (feature: any, iconSize: number) => {
  const [lng, lat] = feature.geometry.coordinates//获取景点经纬度
  
  return new AMap.Marker({
    position: [lng, lat],
    title: feature.properties.name,
    label: {
      content: feature.properties.name,
      direction: 'top',
      offset: new AMap.Pixel(0, -iconSize),
      style: {
        backgroundColor: 'rgba(255,255,255,0.9)',
        borderRadius: '4px',
        fontSize: `${Math.max(10, iconSize/2)}px`,
        fontWeight: 'bold',
        padding: '4px 8px',
        border: '1px solid #1890ff',
        color: '#1890ff',
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
      }
    },
    icon: new AMap.Icon({
      image: MAP_CONFIG.ICON.URL,
      size: new AMap.Size(iconSize, iconSize),
      imageSize: new AMap.Size(iconSize, iconSize)
    }),
    offset: new AMap.Pixel(-iconSize/2, -iconSize),
    anchor: 'bottom-center'
  })
}

// 加载景点数据
const loadScenicSpots = async () => {
  if (!map.value) return
  // 清除所有标记
  clearMarkers()
  isLoading.value = true
  loadError.value = ''
  // 获取当前缩放级别
  try {
    const response = await scenicSpotApi.getGeoJson()//获取景点数据
    const features = normalizeFeatures(response.data)//标准化景点数据
    // 如果景点数据存在，则更新标记大小
    if (features.length > 0) {
      const zoom = map.value.getZoom()
      const iconSize = calculateIconSize(zoom)
      // 遍历景点数据，创建标记
      features.forEach(feature => {
        if (!feature?.geometry?.coordinates) return
        // 创建标记
        const marker = createSpotMarker(feature, iconSize)
        // 如果显示景点，则将标记添加到地图
        if (props.showSpots) {
          marker.setMap(map.value)
        }
        // 点击标记时触发事件
        marker.on('click', () => {
          emit('spotClick', {
            name: feature.properties.name,
            description: feature.properties.description,
            address: feature.properties.address || '成都市',
            openTime: feature.properties.opening_hours || '暂无信息',
            price: feature.properties.ticket_price || '免费',
            imageUrl: feature.properties.images?.[0] || null,
            coordinates: feature.geometry.coordinates
          })
        })
        //   将标记添加到景点数组
        spots.value.push(marker)
      })
    } else {
      loadError.value = '暂无景点数据'
    }
  } catch (error: any) {
    console.error('加载景点数据失败:', error)
    loadError.value = '加载景点数据失败，请刷新页面重试'
  } finally {
    isLoading.value = false
  }
}

// 标准化GeoJSON特征数据
const normalizeFeatures = (data: any) => {
  if (!data || data.type !== 'FeatureCollection') {
    return []
  }
  
  let features = data.features
  
  // 处理对象形式的特征集合
  if (features && typeof features === 'object' && !Array.isArray(features)) {
    features = Object.values(features)
  }
  
  return Array.isArray(features) ? features : []
}

// 更新所有标记的大小
const updateMarkersSize = () => {
  if (!map.value) return
  
  const zoom = map.value.getZoom()
  const iconSize = calculateIconSize(zoom)
  
  spots.value.forEach(marker => {
    const title = marker.getTitle()
    
    // 更新图标
    marker.setIcon(new AMap.Icon({
      image: MAP_CONFIG.ICON.URL,
      size: new AMap.Size(iconSize, iconSize),
      imageSize: new AMap.Size(iconSize, iconSize)
    }))
    
    // 更新偏移量
    marker.setOffset(new AMap.Pixel(-iconSize/2, -iconSize))
    
    // 更新标签样式
    const fontSize = Math.max(12, iconSize/2)
    marker.setLabel({
      content: title,
      direction: 'top',
      offset: new AMap.Pixel(0, -iconSize - 5),
      style: {
        backgroundColor: 'rgba(255,255,255,0.9)',
        borderRadius: '4px',
        fontSize: `${fontSize}px`,
        fontWeight: 'bold',
        padding: '4px 8px',
        border: '1px solid #1890ff',
        color: '#1890ff',
        boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
      }
    })
  })
}

// 监听 showSpots 变化
watch(() => props.showSpots, (show) => {
  spots.value.forEach(marker => {
    if (show) {
      marker.setMap(map.value)
    } else {
      marker.setMap(null)
    }
  })
})

// 开始绘制区域
const startDrawArea = () => {
  if (drawingPolygon.value) {
    map.value.remove(drawingPolygon.value)
  }
  mouseTool.value.polygon({
    strokeColor: '#3eaf7c',
    strokeOpacity: 1,
    strokeWeight: 4,
    fillColor: '#3eaf7c',
    fillOpacity: 0.3,
    strokeStyle: 'dashed'
  })
}

// 停止绘制区域
const stopDrawArea = () => {
  mouseTool.value.close()
}

// 清除区域选择
const clearArea = () => {
  if (drawingPolygon.value) {
    map.value.remove(drawingPolygon.value)
    drawingPolygon.value = null
  }
}

// 处理绘制完成
const handleDrawComplete = (e: any) => {
  drawingPolygon.value = e.obj
  const path = e.obj.getPath()
  
  // 先加载所有景点数据但不显示
  loadScenicSpots().then(() => {
    // 检查每个景点是否在多边形内
    const selectedSpots = spots.value.filter(spot => {
      const position = spot.getPosition()
      return AMap.GeometryUtil.isPointInRing(
        [position.getLng(), position.getLat()],
        path
      )
    })
    
    // 清除不在区域内的景点
    spots.value.forEach(spot => {
      if (!selectedSpots.includes(spot)) {
        spot.remove()
      }
    })
    
    // 只保留选中的景点
    spots.value = selectedSpots
    
    emit('areaSelected', selectedSpots)
  })
  
  mouseTool.value.close()
}

// 居中到指定景点
const centerToSpot = (coordinates: [number, number]) => {
  if (!map.value) return
  map.value.setZoomAndCenter(15, coordinates)
}

// 监听图层变化
watch(() => props.activeLayers, (newLayers, oldLayers) => {
  if (!map.value) return

  // 找出需要添加和移除的图层
  const layersToAdd = newLayers.filter(layer => !oldLayers.includes(layer))
  const layersToRemove = oldLayers.filter(layer => !newLayers.includes(layer))

  // 移除不需要的图层
  layersToRemove.forEach(layer => {
    if (wmsLayers.value[layer]) {
      wmsLayers.value[layer].setMap(null)
      delete wmsLayers.value[layer]
    }
  })

  // 添加新的图层
  layersToAdd.forEach(layer => {
    addWmsLayer(layer)
  })
}, { deep: true })

// 添加 WMS 图层
const addWmsLayer = (layerName: string) => {
  if (!map.value || wmsLayers.value[layerName]) {
    console.log('地图未初始化或图层已存在:', { map: !!map.value, layerExists: !!wmsLayers.value[layerName] })
    return
  }

  console.log('开始加载图层:', layerName)
  // 确保图层名称包含工作空间
  const fullLayerName = layerName.includes(':') ? layerName : `ne:${layerName}`
  // 构建WFS请求URL来获取点位数据
  const wfsUrl = `http://localhost:8080/geoserver/ne/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=${fullLayerName}&outputFormat=application/json`
  console.log('WFS请求URL:', wfsUrl)

  fetch(wfsUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      console.log('WFS响应状态:', response.status)
      return response.json()
    })
    .then(data => {
      console.log('收到WFS数据:', data)
      if (!data.features || !Array.isArray(data.features)) {
        throw new Error('无效的GeoJSON数据格式')
      }

      const markers = data.features.map((feature: any) => {
        if (!feature.geometry || !feature.geometry.coordinates) {
          console.warn('无效的要素数据:', feature)
          return null
        }

        // 确保坐标顺序正确（GeoServer返回的是[经度,纬度]，高德地图也是[经度,纬度]）
        const coordinates = feature.geometry.coordinates
        console.log('创建标记:', { coordinates, name: feature.properties?.name })
        
        const marker = new AMap.Marker({
          position: coordinates,
          title: feature.properties?.name || '',
          label: {
            content: feature.properties?.name || '',
            direction: 'top'
          },
          icon: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png'
        })
        marker.setMap(map.value)
        return marker
      }).filter(Boolean)

      console.log(`成功创建 ${markers.length} 个标记`)
      wmsLayers.value[layerName] = markers
    })
    .catch(error => {
      console.error('加载点位数据失败:', error)
      loadError.value = `加载图层 ${layerName} 失败: ${error.message}`
    })
}

// 移除 WMS 图层
const removeWmsLayer = (layerName: string) => {
  const markers = wmsLayers.value[layerName]
  if (markers) {
    if (Array.isArray(markers)) {
      markers.forEach(marker => marker.setMap(null))
    }
    delete wmsLayers.value[layerName]
  }
}

// 清除所有 WMS 图层
const clearAllWmsLayers = () => {
  Object.keys(wmsLayers.value).forEach(layerName => {
    removeWmsLayer(layerName)
  })
}

// 显示路线
const showRoute = (route: any) => {
  // 清除现有路线
  clearRoute()
  
  // 创建新的路线
  const path = route.path.map((point: any) => [point.lng, point.lat])
  routePolyline.value = new AMap.Polyline({
    path: path,
    strokeColor: '#3eaf7c',
    strokeWeight: 6,
    strokeOpacity: 0.8,
    strokeStyle: 'solid',
    lineJoin: 'round',
    lineCap: 'round',
    zIndex: 50
  })
  
  // 将路线添加到地图
  routePolyline.value.setMap(map.value)
  
  // 调整地图视野以显示整个路线
  map.value.setFitView([routePolyline.value])
  
  // 保存当前路线信息
  currentRoute.value = route.info
}

// 清除路线
const clearRoute = () => {
  if (routePolyline.value) {
    routePolyline.value.setMap(null)
    routePolyline.value = null
  }
  currentRoute.value = null
}

// 处理路线显示
const handleShowRoute = (routeData: any) => {
  console.log('MapView - handleShowRoute 被调用')
  console.log('接收到路线数据:', routeData)
  
  // 清除之前的路线和标记
  if (currentRoute.value) {
    console.log('清除现有路线')
    map.value?.remove([currentRoute.value])
    currentRoute.value = null
  }
  if (startMarker.value) {
    console.log('清除起点标记')
    map.value?.remove([startMarker.value])
    startMarker.value = null
  }
  if (endMarker.value) {
    console.log('清除终点标记')
    map.value?.remove([endMarker.value])
    endMarker.value = null
  }

  if (!map.value) {
    console.error('地图实例未初始化')
    return
  }

  if (!routeData.path || !Array.isArray(routeData.path)) {
    console.error('路线数据格式错误:', routeData)
    return
  }

  console.log('起点坐标:', routeData.startPoint)
  console.log('终点坐标:', routeData.endPoint)
  console.log('路线坐标点数量:', routeData.path.length)

  try {
    // 创建起点标记
    console.log('创建起点标记')
    startMarker.value = new AMap.Marker({
      position: routeData.startPoint,
      icon: new AMap.Icon({
        size: new AMap.Size(25, 34),
        imageSize: new AMap.Size(25, 34),
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/start.png'
      }),
      zIndex: 99
    })

    // 创建终点标记
    console.log('创建终点标记')
    endMarker.value = new AMap.Marker({
      position: routeData.endPoint,
      icon: new AMap.Icon({
        size: new AMap.Size(25, 34),
        imageSize: new AMap.Size(25, 34),
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/end.png'
      }),
      zIndex: 99
    })

    // 根据交通方式设置路线颜色
    const strokeColor = routeData.type === 'transit' ? '#108ee9' : 
                       routeData.type === 'walking' ? '#52c41a' : '#ff4d4f'

    // 创建路线
    console.log('创建路线，路径点数:', routeData.path.length)
    currentRoute.value = new AMap.Polyline({
      path: routeData.path,
      isOutline: true,
      outlineColor: '#ffffff',
      borderWeight: 2,
      strokeWeight: 5,
      strokeColor: strokeColor,
      lineJoin: 'round',
      lineCap: 'round',
      zIndex: 50
    })

    // 添加覆盖物到地图
    map.value.add([startMarker.value, endMarker.value, currentRoute.value])

    // 调整地图视野以包含所有点
    console.log('调整地图视野')
    map.value.setFitView([startMarker.value, endMarker.value, currentRoute.value], {
      padding: [100, 100, 100, 100]
    })

    console.log('路线显示完成')
  } catch (error) {
    console.error('显示路线时发生错误:', error)
  }
}

// 打开路线规划抽屉
const openRouteDrawer = () => {
  console.log('打开路径规划抽屉')
  isDrawerOpen.value = true
}

// 初始化地图
const initMap = async () => {
  const mapContainer = document.getElementById('map')
  if (!mapContainer) return

  const defaultLat = Number(import.meta.env.VITE_MAP_DEFAULT_LAT || 30.67)
  const defaultLng = Number(import.meta.env.VITE_MAP_DEFAULT_LNG || 104.07)
  const defaultZoom = Number(import.meta.env.VITE_MAP_DEFAULT_ZOOM || 12)  // 调整默认缩放级别

  // 创建图层
  const layers = props.mapType === 'satellite' 
    ? [new AMap.TileLayer.Satellite()]
    : [new AMap.TileLayer()]

  // 初始化高德地图
  map.value = new AMap.Map('map', {
    zoom: defaultZoom,
    center: [defaultLng, defaultLat],
    viewMode: '3D',
    pitch: 0,
    rotation: 0,
    layers: layers,
    features: ['bg', 'building', 'point'],  // 移除 'road'
    buildingAnimation: true,
    skyColor: '#1890ff'
  })

  // 添加地图控件
  map.value.addControl(new AMap.Scale())
  map.value.addControl(new AMap.ToolBar({
    position: 'RT'
  }))

  // 初始化鼠标工具
  mouseTool.value = new AMap.MouseTool(map.value)
  mouseTool.value.on('draw', handleDrawComplete)

  // 加载景点数据
  await loadScenicSpots()

  // 添加初始图层
  props.activeLayers.forEach(layer => {
    addWmsLayer(layer)
  })

  // 添加缩放事件监听
  map.value.on('zoomend', () => {
    updateMarkersSize()
  })
  
  // 添加缩放中的事件监听，使图标大小变化更平滑
  let zoomTimer: any = null
  map.value.on('zooming', () => {
    if (zoomTimer) clearTimeout(zoomTimer)
    zoomTimer = setTimeout(() => {
      updateMarkersSize()
    }, 10) // 添加少量延迟以提高性能
  })
}

// 生命周期钩子
onMounted(() => {
  // 设置安全密钥
  window._AMapSecurityConfig = {
    securityJsCode: '27cef49b3ef8fd40f763d9191fd5a637'
  }

  // 加载高德地图 SDK，添加所需插件
  const script = document.createElement('script')
  script.src = `https://webapi.amap.com/maps?v=2.0&key=${import.meta.env.VITE_AMAP_KEY}&plugin=AMap.Scale,AMap.ToolBar,AMap.TileLayer.RoadNet,AMap.MouseTool,AMap.GeometryUtil,AMap.TileLayer.Satellite,AMap.GroundImage,AMap.Driving,AMap.Walking,AMap.Riding,AMap.Transfer`
  script.async = true
  script.onload = () => {
    initMap()
  }
  document.head.appendChild(script)
})

onUnmounted(() => {
  if (mouseTool.value) {
    mouseTool.value.close(true)
    mouseTool.value = null
  }
  if (map.value) {
    map.value.destroy()
    map.value = null
  }
  clearAllWmsLayers()
  clearRoute()
})

// 暴露方法给父组件
defineExpose({
  centerToChengdu,
  loadScenicSpots,
  startDrawArea,
  stopDrawArea,
  clearArea,
  centerToSpot,
  showRoute,
  clearRoute,
  openRouteDrawer
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-width: 0;
  flex: 1 1 auto;
  display: flex;
  margin: 0;
  padding: 0;
  overflow: hidden;
  border-radius: var(--radius-md);
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
}

#map {
  width: 100%;
  height: 100%;
  z-index: 1;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
}

.map-controls {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-btn {
  background: white;
  border: none;
  border-radius: var(--radius-md);
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-btn:hover:not(:disabled) {
  background: var(--primary-light);
  color: white;
  transform: translateY(-2px);
}

.control-btn:active:not(:disabled) {
  transform: translateY(0);
}

.control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.control-btn span {
  position: relative;
}

.control-btn::before {
  content: '🏙️';
  font-size: 16px;
}

.control-btn:nth-child(2)::before {
  content: '🔄';
}

.control-btn:nth-child(3)::before {
  content: '🛰️';
}

.refresh-btn::before {
  content: '🔄';
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  backdrop-filter: blur(2px);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.3);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(239, 68, 68, 0.9);
  color: white;
  padding: 15px 20px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: 1001;
  text-align: center;
  max-width: 80%;
}

.error-message button {
  background-color: white;
  color: #ef4444;
  border: none;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  margin-top: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.error-message button:hover {
  background-color: #f9fafb;
  transform: translateY(-2px);
}

:deep(.popup-content) {
  padding: 10px;
  border-radius: var(--radius-md);
}

:deep(.popup-content h3) {
  margin: 0 0 8px 0;
  color: var(--primary-color);
  font-weight: 600;
}

:deep(.click-popup) {
  text-align: center;
  padding: 8px;
  font-size: 14px;
  color: var(--text-primary);
}

/* 确保 Leaflet 控件样式正确显示 */
:deep(.leaflet-control-zoom) {
  border: none;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

:deep(.leaflet-control-zoom a) {
  background: white;
  color: var(--text-primary);
  width: 36px;
  height: 36px;
  line-height: 36px;
  font-size: 18px;
  font-weight: bold;
  transition: all var(--transition-fast);
}

:deep(.leaflet-control-zoom a:hover) {
  background: var(--primary-light);
  color: white;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 0;
}

:deep(.leaflet-popup-content) {
  margin: 12px;
  line-height: 1.5;
}

:deep(.leaflet-popup-tip) {
  background: white;
  box-shadow: var(--shadow-md);
}

:deep(.leaflet-popup-close-button) {
  padding: 8px;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

:deep(.leaflet-popup-close-button:hover) {
  color: var(--primary-color);
}

:deep(.leaflet-marker-icon) {
  filter: drop-shadow(0 3px 5px rgba(0, 0, 0, 0.2));
  transition: all var(--transition-fast);
}

:deep(.leaflet-marker-icon:hover) {
  transform: scale(1.1) translateY(-5px);
}

:deep(.leaflet-control-scale) {
  border: none;
  box-shadow: var(--shadow-sm);
  padding: 2px 5px;
  border-radius: var(--radius-sm);
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
}
</style>
