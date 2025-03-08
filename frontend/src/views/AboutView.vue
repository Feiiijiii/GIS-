<template>
  <div class="about">
    <div class="about-content">
      <h1>成都市旅游服务系统</h1>
      
      <section class="section">
        <h2>系统简介</h2>
        <p>本系统是一个基于 Web GIS 的成都市旅游服务平台，集成了景点展示、路线规划、周边服务等功能，旨在为游客提供便捷的旅游信息服务。</p>
      </section>

      <section class="section">
        <h2>主要功能</h2>
        <ul>
          <li>
            <strong>景点浏览</strong>
            <p>支持在地图上浏览成都市各大景点，提供景点详细信息、开放时间、门票价格等信息。</p>
          </li>
          <li>
            <strong>周边服务</strong>
            <p>集成了酒店、民宿、餐饮（川菜、火锅、小吃、西餐）、交通（地铁站、公交站、停车场）等配套服务信息。</p>
          </li>
          <li>
            <strong>地图功能</strong>
            <p>支持 2D/3D 视图切换、卫星地图/普通地图切换、区域选择、路线规划等多种地图操作功能。</p>
          </li>
        </ul>
      </section>

      <section class="section">
        <h2>技术架构</h2>
        <ul>
          <li><strong>前端：</strong>Vue 3 + TypeScript + Vite</li>
          <li><strong>地图引擎：</strong>高德地图 JavaScript API</li>
          <li><strong>后端：</strong>Django REST Framework</li>
          <li><strong>数据来源：</strong>
            <ul>
              <li>景点信息：携程网站数据爬取</li>
              <li>周边服务：高德地图 POI 数据</li>
            </ul>
          </li>
        </ul>
      </section>

      <section class="section">
        <h2>使用说明</h2>
        <ol>
          <li>注册/登录系统后即可使用全部功能</li>
          <li>在地图上点击景点图标可查看详细信息</li>
          <li>使用左侧边栏的工具进行区域选择和路线规划</li>
          <li>通过顶部导航栏切换不同的服务类型</li>
        </ol>
      </section>
    </div>
  </div>
</template>

<style scoped>
.about {
  min-height: calc(100vh - var(--nav-height));
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem;
  background-color: var(--background-color);
  overflow-y: auto; /* 添加垂直滚动条 */
}

.about-content {
  max-width: 800px;
  width: 100%;
  background: var(--card-bg);
  padding: 2rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: 2rem; /* 添加底部间距 */
}

h1 {
  color: var(--primary-color);
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
}

.section {
  margin-bottom: 2rem;
}

h2 {
  color: var(--text-primary);
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--primary-color);
}

p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

ul, ol {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

li {
  color: var(--text-secondary);
  margin-bottom: 1rem;
  line-height: 1.6;
}

strong {
  color: var(--text-primary);
  font-weight: 600;
}

@media (max-width: 768px) {
  .about {
    padding: 1rem;
  }
  
  .about-content {
    padding: 1.5rem;
  }
  
  h1 {
    font-size: 1.75rem;
  }
  
  h2 {
    font-size: 1.25rem;
  }
}
</style>
