from todays.models import CompanyToday, IndexToday
from todays.serializers import CompanyTodaySerializer, IndexTodaySerializer
from rest_framework import generics, filters
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from util.permissions import IsOwnerOrReadOnly

class CompanyTodayList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyToday.objects.all()
    serializer_class = CompanyTodaySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class CompanyTodayDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyToday.objects.all()
    serializer_class = CompanyTodaySerializer


class IndexTodayList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexToday.objects.all()
    serializer_class = IndexTodaySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class IndexTodayDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexToday.objects.all()
    serializer_class = IndexTodaySerializer
