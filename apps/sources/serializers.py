from rest_framework import serializers
from .models import (
    Category,
    Source,
    MarkedSource
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def validate_name(value):
        if not value.strip():
            raise serializers.ValidationError("Название категории источника не может быть пустым!")
        return value.strip()


class SourceSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Source
        fields = ('id', 'text', 'link', 'category')

    @staticmethod
    def validate_text(value):
        if not value.strip():
            raise serializers.ValidationError("Текст источника не может быть пустым!")
        return value.strip()

    @staticmethod
    def validate_link(value):
        if not value.strip():
            raise serializers.ValidationError("Адрес ссылки не может быть пустым!")
        return value.strip()


class MarkedSourceSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        source='source',
        queryset=Source.objects.all(),
        write_only=True,
        help_text = 'Source ID'
    )
    class Meta:
        model = MarkedSource
        fields = ('id', 'user', 'source', 'source_id')
        read_only_fields = ('user', 'source')
