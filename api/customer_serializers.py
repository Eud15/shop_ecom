from rest_framework import serializers
from django.contrib.auth.models import User
from .serializers import CartItemSerializer
from .user_utils import get_user_role

class CustomerWithCartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    cart_total = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        default=0
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'date_joined', 'last_login',
            'cart_items', 'cart_total', 'role', 'orders_count',
            'total_spent'
        )

    def get_role(self, obj):
        return get_user_role(obj)

    def get_cart_items(self, obj):
        if hasattr(obj, 'cart') and obj.cart:
            return CartItemSerializer(obj.cart.items.all(), many=True).data
        return []

    def get_cart_total(self, obj):
        if hasattr(obj, 'cart') and obj.cart:
            return sum(
                item.product.price * item.quantity
                for item in obj.cart.items.all()
            )
        return 0