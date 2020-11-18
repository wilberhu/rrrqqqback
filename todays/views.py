from todays.models import CompanyToday, IndexToday
from todays.serializers import CompanyTodaySerializer, IndexTodaySerializer
from rest_framework import generics, status
from rest_framework import permissions
from util.permissions import IsOwnerOrReadOnly

class CompanyTodayList(generics.ListAPIView):
    serializer_class = CompanyTodaySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if(self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return CompanyToday.objects.all()
        else:
            return CompanyToday.objects.all().order_by(self.request.query_params.get('sort'))


class CompanyTodayDetail(generics.RetrieveAPIView):

    queryset = CompanyToday.objects.all()
    serializer_class = CompanyTodaySerializer


    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

class IndexTodayList(generics.ListAPIView):
    serializer_class = IndexTodaySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if(self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return IndexToday.objects.all()
        else:
            return IndexToday.objects.all().order_by(self.request.query_params.get('sort'))


class IndexTodayDetail(generics.RetrieveAPIView):

    queryset = IndexToday.objects.all()
    serializer_class = IndexTodaySerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
