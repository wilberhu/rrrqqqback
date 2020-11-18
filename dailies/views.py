from dailies.models import CompanyDaily, IndexDaily
from dailies.serializers import CompanyDailySerializer, IndexDailySerializer
from rest_framework import generics, status
from rest_framework import permissions
from util.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from django.db import connection
import pandas as pd
import numpy as np
import os

# class CompanyList(generics.ListCreateAPIView):
class CompanyDailyList(generics.ListAPIView):
    serializer_class = CompanyDailySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if(self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return CompanyDaily.objects.all()
        else:
            return CompanyDaily.objects.all().order_by(self.request.query_params.get('sort'))


# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class CompanyDailyDetail(generics.RetrieveAPIView):

    queryset = CompanyDaily.objects.all()
    serializer_class = CompanyDailySerializer


    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

# class CompanyList(generics.ListCreateAPIView):
class IndexDailyList(generics.ListAPIView):
    serializer_class = IndexDailySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)
    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if(self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return IndexDaily.objects.all()
        else:
            return IndexDaily.objects.all().order_by(self.request.query_params.get('sort'))



# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class IndexDailyDetail(generics.RetrieveAPIView):

    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer


    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

from rest_framework import generics, status
from rest_framework import permissions
from util.permissions import IsOwnerOrReadOnly

from rest_framework.response import Response
from django.db import connection



class SqlQuery(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    def post(self, request, *args, **kwargs):
        # training_id = kwargs['pk']
        # if Training.objects.filter(id=training_id).exists():
        #     training = Training.objects.get(id=training_id)
        #     print(training.data_columns)
        #     columns_str = str(training.data_columns).split(",")
        #     columns_str.append(str(training.label_columns))
        #     columns_int = [int(i) for i in columns_str]
        #
        #     dataset = Dataset.objects.get(id=training.dataset_id)
        #     file_path = str(dataset.file)
        #     df = pd.read_csv(os.path.join("media", file_path), index_col=0)
        #     columns = df.columns[columns_int]
        #
        #     return Response({"columns": columns}, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_204_NO_CONTENT)

        cursor = connection.cursor()
        cursor.execute('select * from companies_company')
        # row = cursor.fetchone()  # 返回结果行游标直读向前，读取一条
        rows = cursor.fetchall()  # 读取所有
        results = []
        for row in rows:
            print(row)

        cursor.close()
        return Response({"columns": "123"}, status=status.HTTP_200_OK)
