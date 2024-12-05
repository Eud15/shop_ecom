from django.db.models import Prefetch, Count, Sum
from django.contrib.auth.models import User
from .models import Cart, CartItem, Order

def get_customers_with_carts():
    """
    Get all customers with their cart information
    """
    return User.objects.filter(is_staff=False).select_related(
        'cart'
    ).prefetch_related(
        Prefetch(
            'cart__items',
            queryset=CartItem.objects.select_related('product')
        ),
        'cart__items__product__category'
    ).annotate(
        orders_count=Count('order'),
        total_spent=Sum('order__total_amount')
    )