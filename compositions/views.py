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
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompositionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsObjectOwner,)

    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    def perform_update(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)


class CompositionCalculate(generics.CreateAPIView):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    permission_classes = (IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):
        allfund=request.data["allfund"]
        commission=request.data["commission"] if "commission" in request.data else 0
        acts=request.data["activities"]

        com = {}
        com["allfund"]=int(allfund)
        com["commission"]=int(commission)
        for date in acts:
            com[date["timestamp"]]=date["companies"]
        result=dailyTrader.mainfunc(com)

        return Response(result, status=status.HTTP_201_CREATED)


class TradeCalender(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Composition.objects.all()

    def get(self, request, *args, **kwargs):
        res = {
            "results": dailyTrader.dateRange()
        }
        return Response(res, status=status.HTTP_200_OK)