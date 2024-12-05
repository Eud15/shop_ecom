from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

def get_user_role(user):
    """
    Get the role of a user (staff or customer)
    """
    if user.is_staff:
        return 'staff'
    return 'customer'

def get_user_details(user):
    """
    Get detailed information about a user
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': get_user_role(user),
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'is_active': user.is_active
    }

def check_user_permissions(user, required_role):
    """
    Check if a user has the required role
    """
    if required_role == 'staff' and not user.is_staff:
        return False
    return True