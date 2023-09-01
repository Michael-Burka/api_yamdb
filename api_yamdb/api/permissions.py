from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class OwnerOrAdminOrReadOnly(permissions.BasePermission):
    """Собcтвенник, администратор или только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or request.user.is_admin
            or obj == request.user)


class AdminWriteOnly(permissions.BasePermission):
    """Изменение доступно только администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class AuthorOrStaffWriteOrReadOnly(permissions.BasePermission):
    """Запись для автора, модератора и администратора; чтение для всех."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
