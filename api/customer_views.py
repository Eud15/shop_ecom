from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .customer_serializers import CustomerWithCartSerializer
from .customer_utils import get_customers_with_carts
from .permissions import IsAdminUser

class CustomerManagementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing customers and their carts.
    Only accessible by admin users.
    """
    serializer_class = CustomerWithCartSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return get_customers_with_carts()

    @action(detail=True, methods=['get'])
    def cart_details(self, request, pk=None):
        """Get detailed cart information for a specific customer"""
        customer = self.get_object()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_carts(self, request):
        """Get customers with non-empty carts"""
        customers = self.get_queryset().filter(cart__items__isnull=False).distinct()
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inactive_carts(self, request):
        """Get customers with empty carts"""
        customers = self.get_queryset().filter(cart__items__isnull=True)
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)