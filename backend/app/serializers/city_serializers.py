from rest_framework import serializers
from ..models import City
from rest_framework.validators import UniqueTogetherValidator


class CitySerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'region_name']


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'region']
        validators = [
            UniqueTogetherValidator(
                queryset=City.objects.all(),
                fields=['name', 'region']
            )
        ]
