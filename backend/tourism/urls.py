from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 暂时注释掉文档导入
# from rest_framework.documentation import include_docs_urls
from .views import ScenicSpotViewSet, UserRegisterView, UserLoginView

# 创建路由器
router = DefaultRouter()
router.register(r'scenic_spots', ScenicSpotViewSet)

# API路径
urlpatterns = [
    # 包含路由器生成的URL
    path('', include(router.urls)),
    
    # 暂时注释掉API文档
    # path('docs/', include_docs_urls(
    #     title='成都旅游API',
    #     description='成都市旅游景点数据API'
    # )),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
]