from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    message = 'Редактирование возможно только автором записи.'

    def has_object_permission(self, request, _, obj):
        return ((obj.author == request.user)
                or (request.method in SAFE_METHODS))


class IsAdminOrReadOnly(BasePermission):
    message = 'Редактирование возможно только администратору.'

    def has_permission(self, request, _):
        return (request.method in SAFE_METHODS)
