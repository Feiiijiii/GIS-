# 成都市旅游GIS系统

这是一个基于Django和Vue.js的成都市旅游地理信息系统，提供景点查询、地图显示等功能。

## 项目结构

- `backend/`: Django后端项目
  - `tourism/`: 旅游景点应用
  - `backend/`: Django项目配置
- `frontend/`: Vue.js前端项目
  - `src/`: 源代码
  - `public/`: 静态资源

## 环境要求

### 后端

- Python 3.8+
- Django 4.2+
- PostgreSQL 12+ (with PostGIS)
- GDAL 3.0+

### 前端

- Node.js 16+
- Vue.js 3
- Vite

## 安装与运行

### 后端

1. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. 安装依赖：

```bash
cd backend
pip install -r requirements.txt
```

3. 配置数据库：

确保PostgreSQL和PostGIS已安装，并创建数据库：

```sql
CREATE DATABASE chengdu_tourism;
```

4. 运行迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

5. 加载示例数据：

```bash
python manage.py load_sample_data
```

6. 启动服务器：

```bash
python manage.py runserver
```

或者直接运行批处理脚本（Windows）：

```bash
start_server.bat
```

### 前端

1. 安装依赖：

```bash
cd frontend
npm install
```

2. 启动开发服务器：

```bash
npm run dev
```

## API文档

启动后端服务器后，可以访问以下URL查看API文档：

- http://localhost:8000/api/tourism/docs/

## 主要功能

- 景点搜索
- 地图显示
- 景点详情查看
- 附近景点查询

## 技术栈

### 后端

- Django
- Django REST Framework
- GeoDjango
- PostGIS

### 前端

- Vue.js 3
- Vite
- Leaflet
- Axios 