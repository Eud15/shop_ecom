from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .cart_utils import calculate_cart_total

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True)
#     password_confirm = serializers.CharField(write_only=True, required=True)
#     email = serializers.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'password_confirm')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password_confirm']:
#             raise serializers.ValidationError({
#                 'password_confirm': 'Passwords do not match'
#             })
        
#         try:
#             validate_password(attrs['password'])
#         except ValidationError as e:
#             raise serializers.ValidationError({
#                 'password': list(e)
#             })
            
#         if User.objects.filter(email=attrs['email']).exists():
#             raise serializers.ValidationError({
#                 'email': 'Email already exists'
#             })
            
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user



class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'date_joined', 'last_login', 'total_orders')
        read_only_fields = ('id', 'date_joined', 'last_login')

    def get_total_orders(self, obj):
        return obj.order_set.count()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserDetailSerializer(serializers.ModelSerializer):
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined', 'orders_count', 'total_spent')

    def get_orders_count(self, obj):
        return obj.order_set.count()

    def get_total_spent(self, obj):
        return sum(order.total_amount for order in obj.order_set.filter(status='delivered'))



class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'category', 'category_name', 'name','image_url', 'description', 
                 'price', 'stock', 'created_at', 'updated_at')

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description','image_url', 'created_at', 'products_count', 'products')

    def get_products_count(self, obj):
        return obj.products.count()

class CategoryListSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description','image_url', 'created_at', 'products_count')

    def get_products_count(self, obj):
        return obj.products.count()

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    last_modified = serializers.DateTimeField(source='updated_at', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'items_count', 'created_at', 'last_modified')

    def get_total(self, obj):
        return calculate_cart_total(obj)

    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())

class CartDetailSerializer(CartSerializer):
    user = UserDetailSerializer(read_only=True)
    last_order = serializers.SerializerMethodField()
    
    class Meta(CartSerializer.Meta):
        fields = CartSerializer.Meta.fields + ('user', 'last_order')

    def get_last_order(self, obj):
        last_order = obj.user.order_set.order_by('-created_at').first()
        if last_order:
            return {
                'id': last_order.id,
                'date': last_order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'status': last_order.status,
                'total_amount': last_order.total_amount
            }
        return None

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)
    customer_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_amount', 'items', 'customer_username', 
                 'customer_email', 'created_at', 'updated_at')

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class CustomerWithCartSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    orders_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'last_login', 'cart', 'orders_count',
            'total_spent'
        )
