import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/tourism',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证信息等
    console.log('API请求:', config.url)
    return config
  },
  error => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`API响应成功: ${response.config.url}`, {
      status: response.status,
      data: response.data ? '数据已接收' : '无数据'
    })
    return response
  },
  error => {
    // 增强错误处理
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('API响应错误:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.config?.url
      })
      
      // 根据状态码处理不同的错误情况
      switch (error.response.status) {
        case 401:
          console.error('未授权访问，请检查认证信息')
          break
        case 403:
          console.error('禁止访问，权限不足')
          break
        case 404:
          console.error('请求的资源不存在，请检查API路径')
          break
        case 500:
          console.error('服务器内部错误，请检查后端日志')
          break
        default:
          console.error(`HTTP错误: ${error.response.status}`)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('API无响应:', {
        url: error.config?.url,
        message: '服务器未响应，请检查后端服务是否运行',
        method: error.config?.method,
        baseURL: error.config?.baseURL
      })
    } else {
      // 请求配置出错
      console.error('API请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

// 景点相关API
export const scenicSpotApi = {
  // 获取所有景点
  getAll: () => api.get('/scenic_spots/'),//获取所有景点,后端地址/scenic_spots/
  
  // 搜索景点
  search: (query: string) => {
    console.log('搜索景点:', query)
    return api.get(`/scenic_spots/geojson/?search=${encodeURIComponent(query)}`)
  },
  
  // 获取附近景点
  getNearby: (lat: number, lng: number, radius: number = 5000) => 
    api.get(`/scenic_spots/nearby/?lat=${lat}&lng=${lng}&radius=${radius}`),
  
  // 获取GeoJSON格式的景点数据
  getGeoJson: () => {
    console.log('获取GeoJSON数据')
    return api.get('/scenic_spots/geojson/')
  },
  
  // 获取单个景点详情
  getById: (id: number) => api.get(`/scenic_spots/${id}/`),
  
  // 获取所有景点分类
  getCategories: () => api.get('/scenic_spots/categories/'),

  // 更新景点数据
  updateData: (pageCount: number = 3) => {
    console.log('更新景点数据')
    return api.post('/scenic_spots/update_data/', { page_count: pageCount })
  },

  // 根据偏好过滤景点
  filter: (preferences: any) => {
    console.log('过滤景点:', preferences)
    return api.post('/scenic_spots/filter/', preferences)
  }
}

// 调试信息
console.log('API服务已初始化', {
  baseURL: api.defaults.baseURL,
  timeout: api.defaults.timeout
})

// 导出API实例，以便可以直接使用
export default api 