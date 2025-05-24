from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets,
    status,
    exceptions
)
from .models import (
    Translation,
    FavoriteWord,
    Category,
    PartOfSpeech,
    Word,
    LearnedWord
)
from .serializers import (
    FavoriteWordSerializer,
    CategorySerializer,
    PartOfSpeechSerializer,
    WordSerializer,
    LearnedWordSerializer,
    TranslationSerializer
)


class DictionaryCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class PartOfSpeechViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = PartOfSpeech.objects.all()
    serializer_class = PartOfSpeechSerializer
    pagination_class = None


class DictionaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WordSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'part_of_speech']
    search_fields = ['text']
    queryset = Word.objects.all()

    @action(detail=True, methods=['get'], url_path='translations')
    def translations(self, request, pk=None):
        word = self.get_object()
        translations = Translation.objects.filter(word=word)
        response_data = {
            "word": WordSerializer(word).data,
            "translations": TranslationSerializer(translations, many=True).data
        }
        return Response(response_data)


class FavoriteWordViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteWordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return FavoriteWord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if FavoriteWord.objects.filter(
                user=self.request.user,
                translation=serializer.validated_data['translation']
        ).exists():
            raise exceptions.ValidationError("Это слово уже в избранном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        translation_id = request.query_params.get('translation_id')
        if not translation_id:
            return Response(
                {"detail": "translation_id необходимый параметр!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_word = self.get_queryset().filter(translation_id=translation_id).first()
        if not favorite_word:
            return Response(
                {"detail": "Слово не обнаружено в избранном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        favorite_word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет избранных слов для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} избранных слов"},
            status=status.HTTP_204_NO_CONTENT
        )


class LearnedWordViewSet(viewsets.ModelViewSet):
    serializer_class = LearnedWordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return LearnedWord.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='count')
    def get_learned_count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if LearnedWord.objects.filter(
                user=self.request.user,
                translation=serializer.validated_data['translation']
        ).exists():
            raise exceptions.ValidationError("Это слово уже в изученном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        translation_id = request.query_params.get('translation_id')
        if not translation_id:
            return Response(
                {"detail": "translation_id необходимый параметр!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        learned_word = self.get_queryset().filter(translation_id=translation_id).first()
        if not learned_word:
            return Response(
                {"detail": "Слова нет в изученном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        learned_word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет изученных слов для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} изученных слов"},
            status=status.HTTP_204_NO_CONTENT
        )
