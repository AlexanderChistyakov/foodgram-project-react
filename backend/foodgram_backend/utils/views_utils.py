from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def list(self, _):
    """Получение элементов кверисета в виде списка словарей
    (значение 'result')."""

    serializer = self.serializer_class(self.queryset, many=True)
    data = serializer.data[:]
    return Response(data)


def favorite(_, request, pk, ModelToAdd, ModelToSerialize, SerializerForModel):
    """Добавление записи в избранное, удаление из избранного."""

    user = request.user
    recipe = get_object_or_404(ModelToSerialize, id=pk)
    if request.method == 'POST':
        if not ModelToAdd.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            ModelToAdd.objects.create(user=request.user, recipe=recipe)
            recipes = ModelToSerialize.objects.filter(id=pk).first()
            serializer = SerializerForModel(recipes)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': 'Ошибка добавления записи.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if ModelToAdd.objects.filter(
        user=user,
        recipe=recipe
    ).exists():
        ModelToAdd.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Ошибка. Нет записи в БД для удаления.'},
        status=status.HTTP_400_BAD_REQUEST
    )