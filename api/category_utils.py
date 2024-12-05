from django.db.models import Prefetch
from .models import Category, Product

def get_categories_with_products():
    """
    Get all categories with their associated products
    Using select_related and prefetch_related for optimization
    """
    return Category.objects.prefetch_related(
        Prefetch(
            'products',
            queryset=Product.objects.select_related('category')
        )
    ).all()