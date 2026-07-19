from rest_framework import serializers
from apps.common.validators import validate_email_format, validate_password_strength


class CuratorRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.CharField(validators=[validate_email_format])
    password = serializers.CharField(write_only=True, validators=[validate_password_strength])
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    role = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')


class CuratorLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
