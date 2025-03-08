<template>
  <aside class="info-sidebar">
    <div class="info-header">
      <h2>景点信息</h2>
    </div>
    <div class="info-content" v-if="spot">
      <div class="spot-image" v-if="spot.imageUrl">
        <img :src="spot.imageUrl" :alt="spot.name" />
      </div>
      <div class="spot-info">
        <h3>{{ spot.name }}</h3>
        <p class="spot-desc">{{ spot.description }}</p>
        <div class="spot-details">
          <p><strong>地址：</strong>{{ spot.address }}</p>
          <p><strong>开放时间：</strong>{{ spot.openTime }}</p>
          <p><strong>门票：</strong>{{ spot.price }}</p>
        </div>
      </div>
    </div>
    <div class="no-spot" v-else>
      <p>请在地图上选择或搜索景点查看详细信息</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface SpotInfo {
  name: string
  description: string
  address: string
  openTime: string
  price: string
  imageUrl?: string
}

// 定义props
const props = defineProps<{
  spot: SpotInfo | null
}>()
</script>

<style scoped>
.info-sidebar {
  width: var(--info-sidebar-width, 300px);
  height: 100%;
  background: var(--card-bg);
  box-shadow: -2px 0 15px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  z-index: 10;
  border-left: 1px solid var(--border-color);
  overflow: hidden;
}

.info-header {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  background-color: #2196F3;
  color: white;
}

.info-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.info-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--text-light) transparent;
}

.info-content::-webkit-scrollbar {
  width: 6px;
}

.info-content::-webkit-scrollbar-track {
  background: transparent;
}

.info-content::-webkit-scrollbar-thumb {
  background-color: var(--text-light);
  border-radius: 6px;
}

.spot-image {
  width: 100%;
  height: 220px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-md);
  position: relative;
}

.spot-image::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 70%, rgba(0, 0, 0, 0.3));
  pointer-events: none;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.spot-image:hover img {
  transform: scale(1.05);
}

.spot-info h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
  font-size: 1.5rem;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.5rem;
}

.spot-info h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 50px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px;
}

.spot-desc {
  margin-bottom: 1.5rem;
  line-height: 1.7;
  color: var(--text-secondary);
  font-size: 1rem;
}

.spot-details {
  background: var(--background-color);
  padding: 1.25rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.spot-details p {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: flex-start;
}

.spot-details p:last-child {
  margin-bottom: 0;
}

.spot-details strong {
  color: var(--text-primary);
  min-width: 80px;
  display: inline-block;
}

.no-spot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
  padding: 2rem;
  gap: 1.5rem;
  background: linear-gradient(135deg, var(--background-color), white);
}

.no-spot p {
  font-size: 1.1rem;
  max-width: 250px;
  line-height: 1.6;
}

.no-spot::before {
  content: '🗺️';
  font-size: 3rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .info-sidebar {
    width: 100%;
    position: absolute;
    right: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(100%);
    transition: transform var(--transition-normal);
  }

  .info-sidebar.active {
    transform: translateX(0);
  }
}
</style> 