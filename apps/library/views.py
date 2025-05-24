from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from apps.library.models import (
    Book,
    Sentence,
    CompletedBook,
    Category,
    Bookmark
)
from apps.library.serializers import (
    BookSerializer,
    SentenceSerializer,
    CompletedBookSerializer,
    CategorySerializer,
    BookmarkSerializer
)
from rest_framework import (
    viewsets,
    status,
    filters,
    exceptions
)


class BookCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class LibraryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'author']
    queryset = Book.objects.all()

    @action(detail=True, methods=['get'], url_path='sentences')
    def sentences(self, request, pk=None):
        book = self.get_object()
        sentences = Sentence.objects.filter(book=book)
        response_data = {
            "book": BookSerializer(book).data,
            "sentences": SentenceSerializer(sentences, many=True).data
        }
        return Response(response_data)


class CompletedBookViewSet(viewsets.ModelViewSet):
    serializer_class = CompletedBookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return CompletedBook.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='count')
    def get_completed_count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if CompletedBook.objects.filter(
                user=self.request.user,
                book=serializer.validated_data['book']
        ).exists():
            raise exceptions.ValidationError("Эта книга уже в прочитанном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response(
                {"detail": "book_id необходимый параметр"},
                status=status.HTTP_400_BAD_REQUEST
            )
        completed_book = self.get_queryset().filter(book_id=book_id).first()
        if not completed_book:
            return Response(
                {"detail": "Книга не обнаружена в прочитанном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        completed_book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Не найдены прочитанные книги для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} прочитанных книг"},
            status=status.HTTP_204_NO_CONTENT
        )


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        Bookmark.objects.filter(user=self.request.user, book=book).delete()
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет закладок для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} закладок"},
            status=status.HTTP_204_NO_CONTENT
        )
