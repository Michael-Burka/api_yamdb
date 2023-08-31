from rest_framework import permissions


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


class StaffReadOnlyOrAdminWrite(permissions.BasePermission):
    """Доступ на чтение для персонала, запись только для администратора."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
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
