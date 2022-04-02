# from django.http import JsonResponse
# using django rest framework ...
from rest_framework.decorators import api_view
from rest_framework.response import Response

from baseapp.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/room',
        'GET /api/room/:id',
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request, params):
    room = Room.objects.get(id=params)
    serializer = RoomSerializer(room, many=False)

    return Response(serializer.data)