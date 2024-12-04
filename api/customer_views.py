from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Prefetch, Count, Sum, F
from .models import Cart, Order
from .serializers import CustomerWithCartSerializer

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing customer information with their carts.
    Only accessible by admin users.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CustomerWithCartSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=False).select_related(
            'cart'
        ).prefetch_related(
            Prefetch(
                'cart__items',
                queryset=Cart.objects.prefetch_related('items__product')
            ),
            Prefetch(
                'order_set',
                queryset=Order.objects.order_by('-created_at')
            )
        ).annotate(
            orders_count=Count('order'),
            total_spent=Sum('order__total_amount', filter=F('order__status') == 'delivered')
        )

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get all orders for a specific customer"""
        customer = self.get_object()
        orders = Order.objects.filter(user=customer).order_by('-created_at')
        from .serializers import OrderSerializer
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)