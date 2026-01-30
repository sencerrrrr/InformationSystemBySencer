from rest_framework import serializers
from ..models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class RoleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['name']

    def validate_name(self, value):
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError('Роль с таким названием уже существует')
        return value
