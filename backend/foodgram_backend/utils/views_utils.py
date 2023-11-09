from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from utils import text_constants


def favorite(
        _,
        request,
        pk,
        model_to_add,
        model_to_serialize,
        serializer_model
):
    """Добавление записи в избранное, удаление из избранного."""

    user = request.user
    recipe = get_object_or_404(model_to_serialize, id=pk)
    if request.method == 'POST':
        if not model_to_add.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            model_to_add.objects.create(user=request.user, recipe=recipe)
            serializer = serializer_model(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': text_constants.ADD_ENTRY_ERROR},
            status=status.HTTP_400_BAD_REQUEST
        )
    if model_to_add.objects.filter(
        user=user,
        recipe=recipe
    ).exists():
        model_to_add.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': text_constants.NO_ENTRY},
        status=status.HTTP_400_BAD_REQUEST
    )
