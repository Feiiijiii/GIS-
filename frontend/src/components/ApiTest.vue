<template>
  <div class="api-test">
    <h2>API连接测试</h2>
    
    <div class="config-info">
      <h3>当前配置</h3>
      <div class="config-item">
        <strong>API基础URL:</strong> {{ apiBaseUrl }}
      </div>
      <div class="config-item">
        <strong>代理设置:</strong> {{ proxyConfig }}
      </div>
    </div>
    
    <div class="test-controls">
      <button @click="runAllTests" :disabled="isLoading">运行所有测试</button>
      <button @click="testDirectConnection" :disabled="isLoading">测试直接连接</button>
      <button @click="testProxyConnection" :disabled="isLoading">测试代理连接</button>
      <button @click="testGeoJsonConnection" :disabled="isLoading">测试GeoJSON</button>
      <button @click="testCorsSettings" :disabled="isLoading">测试CORS设置</button>
    </div>
    
    <div v-if="isLoading" class="loading">
      测试中，请稍候...
    </div>
    
    <div v-if="results.length > 0" class="results">
      <h3>测试结果</h3>
      <div 
        v-for="(result, index) in results" 
        :key="index" 
        class="result-item"
        :class="{ 'success': result.success, 'error': !result.success }"
      >
        <div class="result-title">{{ result.title }}</div>
        <div class="result-message">{{ result.message }}</div>
        <pre v-if="result.data" class="result-data">{{ JSON.stringify(result.data, null, 2) }}</pre>
      </div>
    </div>
    
    <div class="troubleshooting">
      <h3>常见问题排查</h3>
      <ul>
        <li>
          <strong>直接连接失败，代理连接成功：</strong> 
          CORS设置可能有问题，但代理正常工作。这种情况下应用可以正常使用。
        </li>
        <li>
          <strong>两种连接都失败：</strong> 
          检查后端服务是否正在运行，以及API路径是否正确。
        </li>
        <li>
          <strong>GeoJSON接口失败：</strong> 
          检查后端是否正确实现了GeoJSON接口，以及数据库中是否有景点数据。
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface TestResult {
  title: string;
  success: boolean;
  message: string;
  data?: any;
}

const isLoading = ref(false);
const results = ref<TestResult[]>([]);
const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL || '/api');
const proxyConfig = ref('代理到 http://localhost:8000');

// 直接连接后端
const testDirectConnection = async () => {
  isLoading.value = true;
  results.value = [];
  
  try {
    const response = await axios.get('http://localhost:8000/api/tourism/scenic_spots/', {
      headers: {
        'Accept': 'application/json'
      }
    });
    results.value.push({
      title: '直接连接测试',
      success: true,
      message: '成功连接到后端API',
      data: response.data
    });
  } catch (error: any) {
    results.value.push({
      title: '直接连接测试',
      success: false,
      message: `连接失败: ${error.message}`,
      data: error.response?.data
    });
  } finally {
    isLoading.value = false;
  }
};

// 通过代理连接
const testProxyConnection = async () => {
  isLoading.value = true;
  results.value = [];
  
  try {
    const response = await axios.get('/api/tourism/scenic_spots/');
    results.value.push({
      title: '代理连接测试',
      success: true,
      message: '成功通过代理连接到后端API',
      data: response.data
    });
  } catch (error: any) {
    results.value.push({
      title: '代理连接测试',
      success: false,
      message: `连接失败: ${error.message}`,
      data: error.response?.data
    });
  } finally {
    isLoading.value = false;
  }
};

// 测试GeoJSON接口
const testGeoJsonConnection = async () => {
  isLoading.value = true;
  results.value = [];
  
  try {
    const response = await axios.get('/api/tourism/scenic_spots/geojson/');
    results.value.push({
      title: 'GeoJSON接口测试',
      success: true,
      message: '成功获取GeoJSON数据',
      data: {
        type: response.data.type,
        features: response.data.features ? `获取到${response.data.features.length}个景点` : '无景点数据'
      }
    });
  } catch (error: any) {
    results.value.push({
      title: 'GeoJSON接口测试',
      success: false,
      message: `获取失败: ${error.message}`,
      data: error.response?.data
    });
  } finally {
    isLoading.value = false;
  }
};

// 测试CORS设置
const testCorsSettings = async () => {
  isLoading.value = true;
  results.value = [];
  
  try {
    // 使用OPTIONS请求测试CORS预检
    const response = await axios({
      method: 'OPTIONS',
      url: 'http://localhost:8000/api/tourism/scenic_spots/',
      headers: {
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'content-type',
        'Origin': window.location.origin
      }
    });
    
    // 检查CORS头信息
    const corsHeaders = {
      'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
      'Access-Control-Allow-Methods': response.headers['access-control-allow-methods'],
      'Access-Control-Allow-Headers': response.headers['access-control-allow-headers']
    };
    
    results.value.push({
      title: 'CORS设置测试',
      success: true,
      message: 'CORS设置正确',
      data: corsHeaders
    });
  } catch (error: any) {
    results.value.push({
      title: 'CORS设置测试',
      success: false,
      message: `CORS设置测试失败: ${error.message}`,
      data: {
        error: error.message,
        response: error.response?.data,
        headers: error.response?.headers
      }
    });
  } finally {
    isLoading.value = false;
  }
};

// 运行所有测试
const runAllTests = async () => {
  isLoading.value = true;
  results.value = [];
  
  await testDirectConnection();
  await testProxyConnection();
  await testGeoJsonConnection();
  await testCorsSettings();
  
  isLoading.value = false;
};

// 检测环境变量
onMounted(() => {
  console.log('API测试组件已加载');
  console.log('API基础URL:', apiBaseUrl.value);
});
</script>

<style scoped>
.api-test {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2, h3 {
  color: #333;
  border-bottom: 2px solid #3b82f6;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

h2 {
  margin-top: 0;
}

h3 {
  margin-top: 25px;
  font-size: 1.2rem;
}

.config-info {
  background-color: #f0f9ff;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.config-item {
  margin-bottom: 8px;
}

.test-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

button:hover:not(:disabled) {
  background-color: #2563eb;
}

button:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.loading {
  padding: 15px;
  background-color: #eff6ff;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
  color: #1e40af;
}

.results {
  margin-top: 20px;
}

.result-item {
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 4px;
}

.success {
  background-color: #ecfdf5;
  border-left: 4px solid #10b981;
}

.error {
  background-color: #fef2f2;
  border-left: 4px solid #ef4444;
}

.result-title {
  font-weight: 600;
  margin-bottom: 5px;
}

.result-message {
  margin-bottom: 10px;
}

.result-data {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  max-height: 200px;
  font-size: 0.9em;
}

.troubleshooting {
  margin-top: 30px;
  background-color: #fffbeb;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #f59e0b;
}

.troubleshooting ul {
  padding-left: 20px;
}

.troubleshooting li {
  margin-bottom: 10px;
}
</style> 