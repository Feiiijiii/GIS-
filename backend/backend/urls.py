"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from tourism.views import UserRegisterView, UserLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将API路径设置为/api/tourism/
    path('api/tourism/', include('tourism.urls')),
    # 添加API根路径重定向
    path('api/', RedirectView.as_view(url='/api/tourism/')),
    # 修改根路径重定向到API路径
    path('', RedirectView.as_view(url='/api/tourism/')),
    # 用户注册和登录路径
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
]
