from rest_framework import serializers
from .models import Category, Product

class ProductInCategorySerializer(serializers.ModelSerializer):
    """Serializer for products when listed within a category"""
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'stock', 'image_url')

class CategoryWithProductsSerializer(serializers.ModelSerializer):
    """Serializer for categories including their products"""
    products = ProductInCategorySerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'image_url', 'products', 'products_count')

    def get_products_count(self, obj):
        return obj.products.count()