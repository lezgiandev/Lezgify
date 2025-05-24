from rest_framework import viewsets, status, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.alphabet.models import (
    Letter,
    LearnedLetter
)
from apps.alphabet.serializers import (
    LetterSerializer,
    LearnedLetterSerializer
)


class LetterListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Letter.objects.all()
    serializer_class = LetterSerializer
    pagination_class = None


class LearnedLetterViewSet(viewsets.ModelViewSet):
    serializer_class = LearnedLetterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return LearnedLetter.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='count')
    def get_count(self, request):
        count = self.get_queryset().count()
        return Response({'count': count}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        if LearnedLetter.objects.filter(
            user=self.request.user,
            letter=serializer.validated_data['letter']
        ).exists():
            raise exceptions.ValidationError("Эта буква уже в изученном!")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        letter_id = request.query_params.get('letter_id')
        if not letter_id:
            return Response(
                {"detail": "letter_id необходимый параметр"},
                status=status.HTTP_400_BAD_REQUEST
            )
        learned_letter = self.get_queryset().filter(letter_id=letter_id).first()
        if not learned_letter:
            return Response(
                {"detail": "Буква не обнаружена в изученном!"},
                status=status.HTTP_404_NOT_FOUND
            )
        learned_letter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Нет букв для удаления"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"detail": f"Удалено {deleted_count} изученных букв"},
            status=status.HTTP_204_NO_CONTENT
        )
