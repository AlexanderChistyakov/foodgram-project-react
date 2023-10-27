from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from user.serializers import CustomUserSerializer

from recipe.serializers import SubscriptionListSerializer
from user.models import Follow, User


class UserListViewSet(views.UserViewSet):
    """Представление пользователей."""
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    @action(
        detail=False,
        url_path='subscriptions',
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Получение подписок и сериализация."""
        authors = User.objects.filter(following__user=request.user)
        serializer = SubscriptionListSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на автора, отписка."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user != author and not Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.create(user=request.user, author=author)
                follows = User.objects.filter(id=id).first()
                serializer = SubscriptionListSerializer(follows)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"errors": "Ошибка подписки."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if user != author and Follow.objects.filter(
                user=user,
                author=author
            ).exists():
                Follow.objects.filter(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Ошибка. Нет записи в БД для удаления."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
