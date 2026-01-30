from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import City
from ..serializers.city_serializers import CitySerializer, CityCreateSerializer


class CitiesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CitiesCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CityCreateSerializer(data=request.data)
        if serializer.is_valid():
            city = serializer.save()
            return Response({
                'message': 'Регион создан',
                'city_id': city.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


