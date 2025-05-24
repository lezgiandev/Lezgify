from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def validate_username(value):
    forbidden_usernames = ['admin', 'root', 'user', 'staff']
    if value.lower() in forbidden_usernames:
        raise ValidationError("This username is prohibited.")
    return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message="Username can contains only letters, numbers and symbols @/./+/-/_"
            ),
            validate_username,
        ],
        min_length=4,
        max_length=150,
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        min_length=8
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        min_length=8
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators = [validate_password],
        style = {'input_type': 'password'},
        min_length = 8
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password typed incorrectly.")
        return value
