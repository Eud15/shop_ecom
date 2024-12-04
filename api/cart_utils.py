from django.db import transaction
from .models import Cart

def get_or_create_cart(user):
    """
    Get the user's cart or create a new one if it doesn't exist
    """
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

def merge_carts(source_cart, destination_cart):
    """
    Merge items from source cart into destination cart
    """
    with transaction.atomic():
        for source_item in source_cart.items.all():
            dest_item, created = destination_cart.items.get_or_create(
                product=source_item.product,
                defaults={'quantity': source_item.quantity}
            )
            
            if not created:
                dest_item.quantity += source_item.quantity
                dest_item.save()
        
        source_cart.items.all().delete()
        source_cart.delete()

def calculate_cart_total(cart):
    """
    Calculate the total price of all items in the cart
    """
    return sum(
        item.product.price * item.quantity
        for item in cart.items.all()
    )