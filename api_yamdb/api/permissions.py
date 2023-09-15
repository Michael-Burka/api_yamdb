from rest_framework import permissions


class AdminWriteOnly(permissions.BasePermission):
    """Изменение доступно только администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_admin
        )


class AuthorOrStaffWriteOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Запись для автора, модератора и администратора; чтение для всех."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class AdminOrReadOnly(AdminWriteOnly):
    """
    Доступ на запись только для администратора.
    Для остальных - только чтение.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or super().has_permission(
            request, view
        )
