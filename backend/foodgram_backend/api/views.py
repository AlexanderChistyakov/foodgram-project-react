from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404

from .models import User, Follow, Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer


@api_view(['POST', 'DELETE'])
@login_required
def subscribe(request, id):
    user = request.user
    author = get_object_or_404(User, id=id)
    if request.method == 'POST':
        if user != author and not Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            Follow.objects.create(user=request.user, author=author)
            return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        Follow.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewset(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
