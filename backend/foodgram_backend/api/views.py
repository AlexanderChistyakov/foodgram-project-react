from uuid import uuid4

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404


from rest_framework import (filters, mixins, permissions, serializers, status,
                            viewsets)
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleReadSerializer, TitleWriteSerializer,
                             TokenSerializer)
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitlesFilter
from .permissions import IsAdminOrReadOnly, IsAdminPermission, IsStuffOrAuthor
from .serializers import RegistrationSerializer, UserSerializer


@api_view(['POST'])
def signup(request):
    serializer = CustomUserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        raise serializers.ValidationError(
            'Некорректное имя или почта'
        )
    confirmation_code = uuid4()
    send_mail('Подтверди регистрацию',
              f'Код верификации: {confirmation_code}',
              None,
              [serializer.validated_data['email']],
              fail_silently=False,)
    user.confirmation_code = confirmation_code
    user.save()
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_access_token(request):
    """"""
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = User.objects.filter(
            username=serializer.validated_data['username']
        )
        if not user.exists():
            return Response(
                serializer.errors, status=status.HTTP_404_NOT_FOUND
            )
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if (
            user.confirmation_code
            == serializer.validated_data['confirmation_code']
        ):
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)})
        return Response(
            {'error': 'Ошибка кода подтверждения'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)