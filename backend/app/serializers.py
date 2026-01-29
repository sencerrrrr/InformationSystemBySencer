from os import write

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Student, Teacher


class HelloSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'user', 'name')


class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'username', 'password', 'email',
            'lastname', 'name', 'middlename',
            'photo', 'birth_date', 'phone', 'group'
        ]

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


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ('id', 'user', 'name')


class TeacherCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        fields = ['name', 'username', 'password']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        teacher = Teacher.objects.create(
            user=user,
            name=validated_data['name']
        )

        return teacher
