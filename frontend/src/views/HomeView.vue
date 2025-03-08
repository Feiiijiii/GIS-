<template>
  <div class="home">
    <SideBar 
      ref="sidebarRef"
      @spot-selected="handleSpotClick"
      @start-draw-area="handleStartDrawArea"
      @stop-draw-area="handleStopDrawArea"
      @clear-area="handleClearArea"
      @show-area-spots="handleShowAreaSpots"
      @show-search-spot="handleShowSearchSpot"
      @open-route-drawer="handleOpenRouteDrawer"
    />
    <MapView 
      ref="mapRef"
      :showSpots="showSpots"
      :mapType="props.mapType"
      @spot-click="handleSpotClick"
      @area-selected="handleAreaSelected"
      @update-map-type="handleUpdateMapType"
    />
    <InfoSideBar 
      v-if="selectedSpot"
      :spot="selectedSpot"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MapView from '@/components/MapView.vue'
import SideBar from '@/components/SideBar.vue'
import InfoSideBar from '@/components/InfoSideBar.vue'

const mapRef = ref<any>(null)
const sidebarRef = ref<any>(null)
const selectedSpot = ref<any>(null)
const showSpots = ref(false)

// 接收地图类型属性
const props = defineProps<{
  mapType: string
}>()

// 处理景点点击
const handleSpotClick = (spot: any) => {
  selectedSpot.value = spot
}

// 处理区域选择开始
const handleStartDrawArea = () => {
  showSpots.value = false // 开始绘制时不显示景点
  selectedSpot.value = null // 清除选中的景点
  if (mapRef.value) {
    mapRef.value.startDrawArea()
  }
}

// 处理区域选择停止
const handleStopDrawArea = () => {
  if (mapRef.value) {
    mapRef.value.stopDrawArea()
  }
}

// 处理区域选择清除
const handleClearArea = () => {
  if (mapRef.value) {
    mapRef.value.clearArea()
  }
  showSpots.value = false // 清除区域时隐藏景点
  selectedSpot.value = null // 清除选中的景点
}

// 处理区域选择完成
const handleAreaSelected = (spots: any[]) => {
  if (sidebarRef.value) {
    sidebarRef.value.handleAreaSelected(spots)
  }
  // 区域选择完成后，不立即显示景点
  showSpots.value = false
}

// 处理显示区域内景点
const handleShowAreaSpots = () => {
  showSpots.value = true // 只有点击"查看景点"按钮时才显示景点
}

// 处理搜索景点显示
const handleShowSearchSpot = async (coordinates: [number, number]) => {
  if (mapRef.value) {
    // 清除现有标记
    await mapRef.value.clearArea()
    // 显示搜索到的景点
    showSpots.value = true
    // 将地图中心移动到该景点
    mapRef.value.centerToSpot(coordinates)
  }
}

// 处理地图类型更新
const handleUpdateMapType = (type: string) => {
  emit('updateMapType', type)
}

// 处理打开路径规划抽屉
const handleOpenRouteDrawer = () => {
  console.log('HomeView - 处理打开路径规划抽屉')
  if (mapRef.value) {
    mapRef.value.openRouteDrawer()
  }
}

const emit = defineEmits(['updateMapType'])
</script>

<style scoped>
.home {
  position: relative;
  height: calc(100vh - var(--nav-height));
  display: flex;
}
</style>
