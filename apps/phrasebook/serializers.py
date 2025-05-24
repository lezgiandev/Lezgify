from rest_framework import serializers
from .models import (
    Category,
    Phrase,
    Translation,
    FavoritePhrase,
    LearnedPhrase
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def validate_name(value):
        if not value.strip():
            raise serializers.ValidationError("Название категории фразы не может быть пустым!")
        return value.strip()


class PhraseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Phrase
        fields = ('id', 'text', 'category')

    @staticmethod
    def validate_text(value):
        if not value.strip():
            raise serializers.ValidationError("Текст фразы не может быть пустым!")
        return value.strip()


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ('id', 'text', 'audio')

    @staticmethod
    def validate_text(value):
        if not value.strip():
            raise serializers.ValidationError("Текст перевода не может быть пустым!")
        return value.strip()

    @staticmethod
    def validate_audio(value):
        if not value.strip():
            raise serializers.ValidationError("Аудио перевода не может быть пустым!")
        return value.strip()


class FavoritePhraseSerializer(serializers.ModelSerializer):
    translation = TranslationSerializer(read_only=True)
    translation_id = serializers.PrimaryKeyRelatedField(
        source='translation',
        queryset=Translation.objects.all(),
        write_only=True,
        help_text='Translation ID'
    )
    class Meta:
        model = FavoritePhrase
        fields = ('id', 'user', 'translation', 'translation_id')
        read_only_fields = ('user', 'translation')


class LearnedPhraseSerializer(serializers.ModelSerializer):
    translation = TranslationSerializer(read_only=True)
    translation_id = serializers.PrimaryKeyRelatedField(
        source='translation',
        queryset=Translation.objects.all(),
        write_only=True,
        help_text='Translation ID'
    )
    class Meta:
        model = LearnedPhrase
        fields = ('id', 'user', 'translation', 'translation_id', 'count')
        read_only_fields = ('user', 'translation', 'count')

    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LearnedPhrase.objects.filter(user=request.user).count()
        return 0
