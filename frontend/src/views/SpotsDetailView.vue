<template>
  <div class="spots-detail">
    <SideBar 
      ref="sidebarRef"
      @spot-selected="handleSpotClick"
      @start-draw-area="handleStartDrawArea"
      @stop-draw-area="handleStopDrawArea"
      @clear-area="handleClearArea"
    />
    <MapView 
      ref="mapRef"
      :showSpots="true"
      :mapType="mapType"
      @spot-click="handleSpotClick"
      @area-selected="handleAreaSelected"
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
import InfoSideBar from '@/components/InfoSideBar.vue'
import SideBar from '@/components/SideBar.vue'

const mapRef = ref<any>(null)
const sidebarRef = ref<any>(null)
const selectedSpot = ref<any>(null)

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
}

// 处理区域选择完成
const handleAreaSelected = (spots: any[]) => {
  if (sidebarRef.value) {
    sidebarRef.value.handleAreaSelected(spots)
  }
}
</script>

<style scoped>
.spots-detail {
  position: relative;
  height: calc(100vh - var(--nav-height));
  display: flex;
}
</style>