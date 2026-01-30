from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Teacher
from .user_serializers import UserSerializer


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'lastname', 'name', 'middlename', 'full_name',
                  'photo', 'birth_date', 'phone']


class TeacherCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        fields = ['username', 'password', 'lastname', 'name', 'middlename',
                  'photo', 'birth_date', 'phone']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher