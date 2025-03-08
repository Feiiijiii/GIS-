from rest_framework import serializers
from .models import ScenicSpot
from django.contrib.auth.models import User

class ScenicSpotSerializer(serializers.ModelSerializer):
    """
    景点序列化器
    """
    # 添加额外字段
    distance = serializers.SerializerMethodField(read_only=True, required=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ScenicSpot
        fields = ('id', 'name', 'longitude', 'latitude', 'description', 'category', 
                 'address', 'opening_hours', 'ticket_price', 'images', 'distance',
                 'created_at', 'updated_at', 'is_favorited')
                 
    def get_distance(self, obj):
        """
        如果请求中包含用户位置，计算到景点的距离
        """
        request = self.context.get('request')
        if not request:
            return None
            
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return None
            
        try:
            from math import radians, sin, cos, sqrt, atan2
            
            # 将经纬度转换为弧度
            lat1, lon1 = radians(float(lat)), radians(float(lng))
            lat2, lon2 = radians(obj.latitude), radians(obj.longitude)
            
            # 地球半径（米）
            R = 6371000
            
            # 使用Haversine公式计算距离
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            # 根据距离返回不同格式
            if distance < 1000:
                return f"{int(distance)}米"
            else:
                return f"{distance/1000:.1f}公里"
        except Exception:
            return None

    def get_is_favorited(self, obj):
        """
        检查当前用户是否已收藏该景点
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False
            
    def validate(self, data):
        """
        验证数据
        """
        # 验证经纬度
        if 'longitude' in data and (data['longitude'] < -180 or data['longitude'] > 180):
            raise serializers.ValidationError("经度必须在-180到180之间")
        if 'latitude' in data and (data['latitude'] < -90 or data['latitude'] > 90):
            raise serializers.ValidationError("纬度必须在-90到90之间")
            
        # 验证票价
        if 'ticket_price' in data and data['ticket_price'] < 0:
            raise serializers.ValidationError("票价不能为负数")
            
        # 验证图片列表
        if 'images' in data and not isinstance(data['images'], list):
            raise serializers.ValidationError("图片必须是URL列表")
            
        return data

# 用户注册序列化器
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("密码长度至少为6个字符")
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            return user
        except Exception as e:
            raise serializers.ValidationError(f"创建用户失败: {str(e)}")

# 用户登录序列化器  
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


