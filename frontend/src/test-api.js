// 测试API连接
import axios from 'axios';

// 直接连接后端
const testDirectConnection = async () => {
  try {
    console.log('尝试直接连接后端...');
    const response = await axios.get('http://localhost:8000/api/tourism/scenic_spots/');
    console.log('直接连接成功:', response.data);
    return true;
  } catch (error) {
    console.error('直接连接失败:', error.message);
    return false;
  }
};

// 通过代理连接
const testProxyConnection = async () => {
  try {
    console.log('尝试通过代理连接后端...');
    const response = await axios.get('/api/tourism/scenic_spots/');
    console.log('代理连接成功:', response.data);
    return true;
  } catch (error) {
    console.error('代理连接失败:', error.message);
    return false;
  }
};

// 测试GeoJSON接口
const testGeoJsonConnection = async () => {
  try {
    console.log('尝试获取GeoJSON数据...');
    const response = await axios.get('/api/tourism/scenic_spots/geojson/');
    console.log('GeoJSON数据获取成功:', response.data);
    return true;
  } catch (error) {
    console.error('GeoJSON数据获取失败:', error.message);
    return false;
  }
};

// 运行测试
const runTests = async () => {
  console.log('=== API连接测试开始 ===');
  
  const directResult = await testDirectConnection();
  const proxyResult = await testProxyConnection();
  const geoJsonResult = await testGeoJsonConnection();
  
  console.log('=== 测试结果 ===');
  console.log('直接连接:', directResult ? '成功' : '失败');
  console.log('代理连接:', proxyResult ? '成功' : '失败');
  console.log('GeoJSON数据:', geoJsonResult ? '成功' : '失败');
  
  console.log('=== API连接测试结束 ===');
};

// 导出测试函数
export { runTests }; 