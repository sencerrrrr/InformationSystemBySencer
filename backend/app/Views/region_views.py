from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Region
from ..serializers.region_serializers import RegionSerializer, RegionCreateSerializer

class RegionsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        region = Region.objects.all()
        serializer = RegionSerializer(region, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegionsCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegionCreateSerializer(data=request.data)
        if serializer.is_valid():
            region = serializer.save()
            return Response({
                'message': 'Регион создан',
                'region_id': region.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

