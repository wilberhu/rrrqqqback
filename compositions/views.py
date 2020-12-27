from compositions.models import Composition
from compositions.serializers import CompositionSerializer
from rest_framework import generics

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import renderers, status
from rest_framework.response import Response

from back_test import dailyTrader


class CompositionList(generics.ListCreateAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer
    ordering_fields = '__all__'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(self.request.user)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompositionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsObjectOwner,)

    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer


class CompositionCalculate(generics.CreateAPIView):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    permission_classes = (IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):
        stock=request.data["stock"]
        acts=request.data["activities"]

        com = {}
        com["stock"]=int(stock)
        for date in acts:
            com[date["timestamp"]]=date["companies"]
        result=dailyTrader.mainfunc(com)

        return Response(result, status=status.HTTP_201_CREATED)