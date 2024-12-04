from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Prefetch
from .models import Cart, CartItem, Product, Order
from .serializers import CartSerializer, CartItemSerializer, CartDetailSerializer
from .cart_utils import get_or_create_cart
from .permissions import IsAdminOrOwner

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        queryset = Cart.objects.prefetch_related(
            'items', 
            'items__product',
            'items__product__category',
            Prefetch(
                'user__order_set',
                queryset=Order.objects.order_by('-created_at'),
                to_attr='recent_orders'
            )
        )
        
        if self.request.user.is_staff:
            return queryset.all()
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'current'] or self.request.user.is_staff:
            return CartDetailSerializer
        return CartSerializer

    def get_object(self):
        """Get cart by ID for admin or current user's cart"""
        if self.kwargs.get('pk') and self.request.user.is_staff:
            return get_object_or_404(Cart, pk=self.kwargs['pk'])
        return get_or_create_cart(self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current user's cart with detailed information"""
        cart = get_or_create_cart(request.user)
        serializer = CartDetailSerializer(cart, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def user_cart(self, request, pk=None):
        """Get detailed cart information for a specific user (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user = User.objects.get(pk=pk)
            cart = get_or_create_cart(user)
            serializer = CartDetailSerializer(cart, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to the current user's cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity > product.stock:
            return Response(
                {'error': 'Not enough stock available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity = min(cart_item.quantity + quantity, product.stock)
            cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from the current user's cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', None) or 0)

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )
            
            if quantity and quantity < cart_item.quantity:
                cart_item.quantity -= quantity
                cart_item.save()
            else:
                cart_item.delete()

        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from the current user's cart"""
        cart = self.get_object()
        cart.items.all().delete()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)