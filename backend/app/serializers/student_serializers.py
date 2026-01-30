from rest_framework import serializers
from django.contrib.auth.models import User
from .user_serializers import UserSerializer
from ..models import Student


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    course_display = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'lastname', 'name', 'middlename', 'full_name',
                  'photo', 'birth_date', 'phone', 'city', 'group', 'group_name',
                  'course', 'course_display']


class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['username', 'password', 'lastname', 'name',
                  'middlename', 'photo', 'birth_date', 'phone', 'group']

    def validate_photo(self, value):
        if value and hasattr(value, 'size'):
            max_size = 10 * 1024 * 1024  # 10 MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f'Файл слишком большой. Максимальный размер: 10MB'
                )
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        student = Student.objects.create(user=user, **validated_data)
        return student