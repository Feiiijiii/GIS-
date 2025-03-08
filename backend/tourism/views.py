from rest_framework import viewsets, filters, generics
from django.db.models import Q, F
from .models import ScenicSpot
from .serializers import ScenicSpotSerializer, UserRegisterSerializer, UserLoginSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .scraper import update_scenic_spots
from math import radians, sin, cos, sqrt, atan2
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# 景点视图集
class ScenicSpotViewSet(viewsets.ModelViewSet):
    queryset = ScenicSpot.objects.all()
    serializer_class = ScenicSpotSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category', 'address']
    ordering_fields = ['name', 'created_at', 'ticket_price']
    ordering = ['name']

    @action(detail=False, methods=['post'])
    def update_data(self, request):
        """触发爬虫更新景点数据"""
        try:
            # 获取请求中的页数参数，默认为3页
            page_count = request.data.get('page_count', 3)
            try:
                page_count = int(page_count)
                if page_count <= 0:
                    page_count = 3
            except (ValueError, TypeError):
                page_count = 3
                
            # 调用爬虫更新数据
            updated_count = update_scenic_spots(page_count=page_count)
            
            return Response({
                'status': 'success',
                'message': f'成功更新{updated_count}个景点数据',
                'data': {
                    'updated_count': updated_count,
                    'page_count': page_count
                }
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"爬虫更新数据出错: {str(e)}\n{error_trace}")
            
            return Response({
                'status': 'error',
                'message': f'更新数据失败：{str(e)}',
                'error_detail': str(e)
            }, status=500)

    @action(detail=False, methods=['post'])
    def filter(self, request):
        """根据用户偏好过滤景点"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'筛选景点时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        """
        统一的查询过滤逻辑
        支持 URL 参数过滤和用户偏好过滤
        """
        queryset = ScenicSpot.objects.all()
        
        # 从请求体获取用户偏好（用于路线规划）
        if self.request.method == 'POST' and self.action == 'filter':
            preferences = self.request.data.get('preferences', [])
            budget = self.request.data.get('budget', 'medium')
            
            if preferences:
                queryset = queryset.filter(category__in=preferences)
                
            if budget == 'low':
                queryset = queryset.filter(Q(ticket_price__lte=100) | Q(ticket_price__isnull=True))
            elif budget == 'medium':
                queryset = queryset.filter(Q(ticket_price__lte=200) | Q(ticket_price__isnull=True))
            
            return queryset[:15]  # 限制返回数量用于路线规划
        
        # URL 参数过滤（用于普通查询）
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            try:
                queryset = queryset.filter(ticket_price__gte=float(min_price))
            except ValueError:
                pass
                
        if max_price:
            try:
                queryset = queryset.filter(ticket_price__lte=float(max_price))
            except ValueError:
                pass
                
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) | 
                Q(address__icontains=search) |
                Q(category__icontains=search)
            )
        
        return queryset

    # 获取附近景点
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        获取指定坐标附近的景点
        参数:
        - lat: 纬度
        - lng: 经度
        - radius: 半径(米)，默认5000米
        """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 5000))  # 默认5公里

        if not lat or not lng:
            return Response({'error': '请提供经纬度参数'}, status=400)

        try:
            lat = float(lat)
            lng = float(lng)
            
            # 将所有景点的距离计算出来
            spots = []
            for spot in ScenicSpot.objects.all():
                # 使用Haversine公式计算距离
                lat1, lon1 = radians(lat), radians(lng)
                lat2, lon2 = radians(spot.latitude), radians(spot.longitude)
                
                # 地球半径（米）
                R = 6371000
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * atan2(sqrt(a), sqrt(1-a))
                distance = R * c
                
                if distance <= radius:
                    spots.append(spot)
            
            serializer = self.get_serializer(spots, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError) as e:
            return Response({'error': f'无效的经纬度格式: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'error': f'查询附近景点时出错: {str(e)}'}, status=500)

    # 获取所有景点的GeoJSON格式数据
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """
        获取所有景点的GeoJSON格式数据
        可选参数:
        - category: 按分类过滤
        - search: 搜索关键词
        """
        try:
            # 获取搜索参数
            search_query = request.query_params.get('search', '')
            category = request.query_params.get('category', '')
            
            # 构建基础查询集
            spots = self.queryset
            
            # 应用搜索过滤
            if search_query:
                spots = spots.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(address__icontains=search_query)
                )
            
            # 应用分类过滤
            if category:
                spots = spots.filter(category=category)
            
            # 构建GeoJSON特性集合
            features = []
            for spot in spots:
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [spot.longitude, spot.latitude]
                    },
                    'properties': {
                        'id': spot.id,
                        'name': spot.name,
                        'description': spot.description,
                        'category': spot.category,
                        'address': spot.address,
                        'opening_hours': spot.opening_hours,
                        'ticket_price': float(spot.ticket_price) if spot.ticket_price else 0,
                        'images': spot.images
                    }
                }
                features.append(feature)
            
            # 返回GeoJSON格式
            return Response({
                'type': 'FeatureCollection',
                'features': features
            })
        except Exception as e:
            import traceback
            print(f"获取GeoJSON数据时出错: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'获取GeoJSON数据时出错: {str(e)}'}, status=500)
    # 获取所有景点分类
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有景点分类"""
        try:
            categories = ScenicSpot.objects.values_list('category', flat=True).distinct()
            return Response(list(categories))
        except Exception as e:
            return Response({'error': f'获取分类列表时出错: {str(e)}'}, status=500)
    # 获取景点详情
    def retrieve(self, request, *args, **kwargs):
        """重写retrieve方法，增加错误处理"""
        try:
            return super().retrieve(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return Response({'error': '找不到指定的景点'}, status=404)
        except Exception as e:
            return Response({'error': f'获取景点详情时出错: {str(e)}'}, status=500)
    # 收藏或取消收藏景点
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """收藏或取消收藏景点"""
        spot = self.get_object()
        user = request.user
        
        if spot.favorited_by.filter(id=user.id).exists():
            # 如果已经收藏了，就取消收藏
            spot.favorited_by.remove(user)
            return Response({'status': 'unfavorited'})
        else:
            # 如果没有收藏，就添加收藏
            spot.favorited_by.add(user)
            return Response({'status': 'favorited'})
    # 获取用户的收藏列表
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        """获取用户的收藏列表"""
        spots = ScenicSpot.objects.filter(favorited_by=request.user).order_by('-created_at')
        serializer = self.get_serializer(spots, many=True)
        return Response(serializer.data)
    # 检查当前景点是否已被用户收藏
    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def is_favorited(self, request, pk=None):
        """检查当前景点是否已被用户收藏"""
        spot = self.get_object()
        is_favorited = spot.favorited_by.filter(id=request.user.id).exists()
        return Response({'is_favorited': is_favorited})

# 用户注册视图  
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)

# 用户登录视图    
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            return Response({"message": "登录成功"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_400_BAD_REQUEST)
