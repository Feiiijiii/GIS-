@echo off
echo 正在启动成都旅游GIS后端服务...

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 运行数据库迁移
python manage.py makemigrations
python manage.py migrate

REM 加载示例数据
python manage.py load_sample_data

REM 启动服务器
python manage.py runserver 0.0.0.0:8000

pause 