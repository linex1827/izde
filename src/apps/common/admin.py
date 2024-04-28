from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_moderator

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_moderator
