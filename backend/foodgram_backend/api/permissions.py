from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    message = 'Редактирование возможно только автором записи.'

    def has_object_permission(self, request, _, obj):
        return ((obj.author == request.user)
                or (request.method in SAFE_METHODS))


class ThisUserOrAdmin(BasePermission):
    message = 'Редактировать можно только свой профиль.'

    def has_permission(self, request, view):
        return (request.user.is_staff
                or request.user == view.kwargs.get('id')
                or (request.method in SAFE_METHODS))
