from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Translation,
    FavoritePhrase,
    Category,
    Phrase,
    LearnedPhrase
)
from .serializers import (
    FavoritePhraseSerializer,
    CategorySerializer,
    PhraseSerializer,
    LearnedPhraseSerializer,
    TranslationSerializer
)
from rest_framework import (
    viewsets,
    status,
    exceptions
)


class PhrasebookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class PhrasebookViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PhraseSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', ]
    search_fields = ['text']
    queryset = Phrase.objects.all()

    @action(detail=True, methods=['get'], url_path='translations')
    def translations(self, request, pk=None):
        phrase = self.get_object()
        translations = Translation.objects.filter(phrase=phrase)
        response_data = {
            "phrase": PhraseSerializer(phrase).data,
            "translations": TranslationSerializer(translations, many=True).data
        }
        return Response(response_data)


class FavoritePhraseViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritePhraseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return FavoritePhrase.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if FavoritePhrase.objects.filter(
                user=self.request.user,
                translation=serializer.validated_data['translation']
        ).exists():
            raise exceptions.ValidationError("Эта фраза уже в избранном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        translation_id = request.query_params.get('translation_id')
        if not translation_id:
            return Response(
                {"detail": "translation_id необходимый параметр!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_phrase = self.get_queryset().filter(translation_id=translation_id).first()
        if not favorite_phrase:
            return Response(
                {"detail": "Фраза не обнаружена в избранном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        favorite_phrase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет избранных фраз для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} избранных фраз"},
            status=status.HTTP_204_NO_CONTENT
        )


class LearnedPhraseViewSet(viewsets.ModelViewSet):
    serializer_class = LearnedPhraseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return LearnedPhrase.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='count')
    def get_learned_count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if LearnedPhrase.objects.filter(
                user=self.request.user,
                translation=serializer.validated_data['translation']
        ).exists():
            raise exceptions.ValidationError("Эта фраза уже в изученном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        translation_id = request.query_params.get('translation_id')
        if not translation_id:
            return Response(
                {"detail": "translation_id необходимый параметр!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        learned_phrase = self.get_queryset().filter(translation_id=translation_id).first()
        if not learned_phrase:
            return Response(
                {"detail": "Фразы нет в изученном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        learned_phrase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет изученных фраз для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} изученных фраз"},
            status=status.HTTP_204_NO_CONTENT
        )
