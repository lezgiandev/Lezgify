from rest_framework import serializers
from .models import (
    Book,
    Sentence,
    CompletedBook,
    Category,
    Bookmark
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def validate_name(value):
        if not value.strip():
            raise serializers.ValidationError("Название категории книги не может быть пустым!")
        return value.strip()


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'category', 'logo')

    @staticmethod
    def validate_title(value):
        if not value.strip():
            raise serializers.ValidationError("Название книги не может быть пустым!")
        return value.strip()

    @staticmethod
    def validate_author(value):
        if not value.strip():
            raise serializers.ValidationError("Имя автора не может быть пустым!")
        return value.strip()

    @staticmethod
    def validate_logo(value):
        if not value.strip():
            raise serializers.ValidationError("Логотип не может быть пустым!")
        return value.strip()


class SentenceSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    class Meta:
        model = Sentence
        fields = ('id', 'text', 'audio', 'translate', 'book')

    @staticmethod
    def validate_text(value):
        if not value.strip():
            raise serializers.ValidationError("Текст предложения не может быть пустым!")
        return value.strip()

    @staticmethod
    def validate_audio(value):
        if not value.strip():
            raise serializers.ValidationError("Озвучка предложения не может быть пустой!")
        return value.strip()

    @staticmethod
    def validate_translate(value):
        if not value.strip():
            raise serializers.ValidationError("Перевод предложения не может быть пустым!")
        return value.strip()


class CompletedBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        source='book',
        queryset=Book.objects.all(),
        write_only=True,
        help_text='Book ID'
    )
    class Meta:
        model = CompletedBook
        fields = ('id', 'user', 'book', 'book_id')
        read_only_fields = ('user', 'book')


class BookmarkSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    sentence = SentenceSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        source='book',
        queryset=Book.objects.all(),
        write_only=True,
        help_text='Book ID'
    )
    sentence_id = serializers.PrimaryKeyRelatedField(
        source='sentence',
        queryset=Sentence.objects.all(),
        write_only=True,
        help_text='Sentence ID'
    )
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'book', 'sentence', 'book_id', 'sentence_id')
        read_only_fields = ('user', 'book', 'sentence')
