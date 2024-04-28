from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.vendor.id == request.user.vendor.id