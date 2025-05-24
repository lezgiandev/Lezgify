from rest_framework import serializers
from .models import (
    Category,
    Word,
    Translation,
    FavoriteWord,
    PartOfSpeech,
    Origin,
    LearnedWord
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def validate_name(value):
        if not value.strip():
            raise serializers.ValidationError("Название категории слова не может быть пустым!")
        return value.strip()


class PartOfSpeechSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartOfSpeech
        fields = '__all__'

    @staticmethod
    def validate_name(value):
        if not value.strip():
            raise serializers.ValidationError("Название части речи не может быть пустым!")
        return value.strip()


class WordSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    part_of_speech = PartOfSpeechSerializer()
    class Meta:
        model = Word
        fields = ('id', 'text', 'category', 'part_of_speech')

    @staticmethod
    def validate_text(value):
        if not value.strip():
            raise serializers.ValidationError("Текст слова не может быть пустым!")
        return value.strip()


class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = '__all__'

    @staticmethod
    def validate_language(value):
        if not value.strip():
            raise serializers.ValidationError("Название языка происхождения не может быть пустым!")
        return value.strip()


class TranslationSerializer(serializers.ModelSerializer):
    origin = OriginSerializer()
    class Meta:
        model = Translation
        fields = ('id', 'text', 'audio', 'origin')

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


class FavoriteWordSerializer(serializers.ModelSerializer):
    translation = TranslationSerializer(read_only=True)
    translation_id = serializers.PrimaryKeyRelatedField(
        source='translation',
        queryset=Translation.objects.all(),
        write_only=True,
        help_text='Translation ID'
    )
    class Meta:
        model = FavoriteWord
        fields = ('id', 'user', 'translation', 'translation_id')
        read_only_fields = ('user', 'translation')


class LearnedWordSerializer(serializers.ModelSerializer):
    translation = TranslationSerializer(read_only=True)
    translation_id = serializers.PrimaryKeyRelatedField(
        source='translation',
        queryset=Translation.objects.all(),
        write_only=True,
        help_text='Translation ID'
    )
    class Meta:
        model = LearnedWord
        fields = ('id', 'user', 'translation', 'translation_id', 'count')
        read_only_fields = ('user', 'translation', 'count')

    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LearnedWord.objects.filter(user=request.user).count()
        return 0
