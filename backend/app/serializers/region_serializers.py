from rest_framework import serializers
from ..models import Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class RegionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']

    def validate_name(self, value):
        if Region.objects.filter(name=value).exists():
            raise serializers.ValidationError('Регион с таким названием уже существует')
        return value
