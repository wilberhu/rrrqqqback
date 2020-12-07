from dailies.models import CompanyDaily, IndexDaily
from dailies.serializers import CompanyDailySerializer, IndexDailySerializer
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from util.permissions import IsOwnerOrReadOnly

# class CompanyList(generics.ListCreateAPIView):
class CompanyDailyList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDaily.objects.all()
    serializer_class = CompanyDailySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class CompanyDailyDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDaily.objects.all()
    serializer_class = CompanyDailySerializer


# class CompanyList(generics.ListCreateAPIView):
class IndexDailyList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class IndexDailyDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer
