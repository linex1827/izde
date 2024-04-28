from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    VENDORS_METHODS = ["GET", "HEAD", "OPTIONS", "POST", "DELETE"]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if hasattr(request.user, "vendor") and request.method in self.VENDORS_METHODS:
            return True
        return False


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.vendor.id == request.user.vendor.id
