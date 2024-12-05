from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category
from .category_serializers import CategoryWithProductsSerializer
from .category_utils import get_categories_with_products

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing categories.
    List and retrieve actions are public.
    Create, update, and delete actions require staff privileges.
    """
    serializer_class = CategoryWithProductsSerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return get_categories_with_products()

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products for a specific category"""
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response(serializer.data)