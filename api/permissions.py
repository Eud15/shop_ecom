from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart to view/edit it.
    Admin users can access everything.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.is_staff:
            return True
            
        # Users can only access their own cart
        return obj.user == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff