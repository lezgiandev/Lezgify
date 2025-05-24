from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from apps.sources.models import (
    Category,
    Source,
    MarkedSource
)
from apps.sources.serializers import (
    CategorySerializer,
    SourceSerializer,
    MarkedSourceSerializer
)
from rest_framework import (
    viewsets,
    filters,
    status, exceptions
)


class SourceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SourceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['text']
    queryset = Source.objects.all()


class MarkedSourceViewSet(viewsets.ModelViewSet):
    serializer_class = MarkedSourceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return MarkedSource.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if MarkedSource.objects.filter(
                user=self.request.user,
                source=serializer.validated_data['source']
        ).exists():
            raise exceptions.ValidationError("Этот источник уже в отмеченном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        source_id = request.query_params.get('source_id')
        if not source_id:
            return Response(
                {"detail": "source_id необходимый параметр!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        marked_source = self.get_queryset().filter(source_id=source_id).first()
        if not marked_source:
            return Response(
                {"detail": "Источник не обнаружен в добавленном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        marked_source.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет отмеченных источников для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} отмеченных источников!"},
            status=status.HTTP_204_NO_CONTENT
        )
