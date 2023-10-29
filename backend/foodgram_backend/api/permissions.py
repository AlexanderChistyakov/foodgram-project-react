from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    message = 'Редактирование возможно только автором записи.'

    def has_object_permission(self, request, _, obj):
        return ((obj.author == request.user)
                or (request.method in SAFE_METHODS))
