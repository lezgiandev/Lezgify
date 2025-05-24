from rest_framework import serializers
from apps.alphabet.models import (
    Letter,
    LearnedLetter
)


class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = '__all__'

    @staticmethod
    def validate_letter(value):
        if not value.strip():
            raise serializers.ValidationError("Название буквы не может быть пустым!")
        return value.strip()


class LearnedLetterSerializer(serializers.ModelSerializer):
    letter = LetterSerializer(read_only=True)
    letter_id = serializers.PrimaryKeyRelatedField(
        source='letter',
        queryset=Letter.objects.all(),
        write_only=True,
        help_text='Letter ID'
    )
    class Meta:
        model = LearnedLetter
        fields = ('id', 'user', 'letter', 'letter_id', 'count')
        read_only_fields = ('user', 'letter', 'count')

    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LearnedLetter.objects.filter(user=request.user).count()
        return 0
