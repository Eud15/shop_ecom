from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    UserViewSet,
    get_user_role,
    
)
from .cart_views import CartViewSet
from .category_views import CategoryViewSet
# from .customer_views import CustomerViewSet
from .customer_views import CustomerManagementViewSet
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
# router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet)
# router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'customers', CustomerManagementViewSet, basename='customer-management')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/role/', get_user_role, name='user-role'),
]