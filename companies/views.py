from companies.models import Company, Index
from companies.serializers import CompanySerializer, IndexSerializer, CompanySimpleSerializer
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework import authentication
from django_filters.rest_framework import DjangoFilterBackend
from util.permissions import IsOwnerOrReadOnly
from django.db import connection
from django.core import serializers
import pandas as pd
import numpy as np
import os
import re
import datetime
import django_filters.rest_framework

hist_data_path = 'tushare_data/data/hist_data/'
index_hist_data_path = 'tushare_data/data/index_hist_data/'
# hist_data_length = -780
hist_data_length = 0

# class CompanyList(generics.ListCreateAPIView):
class CompanyList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name']

    # '^' Starts-with search.
    # '=' Exact matches.
    # '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
    # '$' Regex search.
    search_fields = ['ts_code', 'name']
    ordering_fields = '__all__'

# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class CompanyDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_object(self):
        symbol = self.kwargs['pk']
        return Company.objects.filter(symbol=symbol).first()

class CompanyAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Company.objects.all().only('ts_code', 'name')
    serializer_class = CompanySimpleSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name']
    search_fields = ['ts_code', 'name']
    ordering_fields = ['ts_code', 'name']

    pagination_class = None


class CompanyHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            company = Company.objects.get(ts_code=kwargs['ts_code'])
        except Company.DoesNotExist:
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        file_path = hist_data_path + company.ts_code + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'company_code': company.ts_code, 'company_name': company.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)

class IndexList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Index.objects.all()
    serializer_class = IndexSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name']
    search_fields = ['ts_code', 'name']
    ordering_fields = '__all__'

# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class IndexDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Index.objects.all()
    serializer_class = IndexSerializer

    def get_object(self):
        ts_code = self.kwargs['pk']
        return Index.objects.filter(ts_code=ts_code).first()

class IndexAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Index.objects.all().only('ts_code', 'name')
    serializer_class = CompanySimpleSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name']
    search_fields = ['ts_code', 'name']
    ordering_fields = ['ts_code', 'name']

    pagination_class = None

class IndexHistData(generics.GenericAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [ authentication.BasicAuthentication ]

    def get(self, request, *args, **kwargs):
        try:
            index = Index.objects.get(ts_code=kwargs['ts_code'])
        except Index.DoesNotExist:
            return Response({"code": 20004, "message": "index doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        file_path = index_hist_data_path + index.ts_code + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "index doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'index_code': index.ts_code, 'index_name': index.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)


class CloseData(generics.GenericAPIView):
    # def get(self, request, *args, **kwargs):
    #     return Response({"detail": "Method \"GET\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [ authentication.BasicAuthentication ]

    def post(self, request, *args, **kwargs):
        close_data_list = []
        companyCode = []
        companyName = []
        type = []

        if 'ts_code' not in request.data:
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        codes = re.split("[\n,; ]", request.data['ts_code'])

        if len(codes) <= 0 or len(codes) > 10:
            return Response({"code": 20000,
                             'ts_code_list': companyCode,
                             'name_list': companyName,
                             'type_list': type,
                             'time_line': [],
                             'close_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

        condtions = {}
        if 'date__lte' in request.query_params:
            condtions['date__lte'] = request.query_params['date__lte'].replace("-", "")
        else:
            condtions['date__lte']= None

        if 'date__gte' in request.query_params:
            condtions['date__gte'] = request.query_params['date__gte'].replace("-", "")
        else:
            condtions['date__gte']= None

        for code in codes:
            code = code.strip()
            if code == "":
                continue
            elif Company.objects.filter(ts_code=code).exists():
                company = Company.objects.get(ts_code=code)
                file_path = hist_data_path + company.ts_code + '.csv'
                tmp_type = 0
            elif Index.objects.filter(ts_code=code).exists():
                company = Index.objects.get(ts_code=code)
                file_path = index_hist_data_path + company.ts_code + '.csv'
                tmp_type = 1
            else:
                continue

            if not os.path.exists(file_path):
                continue

            companyCode.append(company.ts_code)
            companyName.append(company.name)
            type.append(tmp_type)

            h_data = pd.read_csv(file_path, dtype={"close": float})[['trade_date', 'close']]
            h_data.index = h_data['trade_date']
            h_data = h_data['close']

            h_data = h_data.loc[condtions['date__gte']: condtions['date__lte']]

            close_data_list.append(h_data)
        if len(close_data_list) == 0:
            return Response({"code": 20000,
                             'ts_code_list': companyCode,
                             'name_list': companyName,
                             'type_list': type,
                             'time_line': [],
                             'close_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

        df = pd.concat(close_data_list, axis=1).fillna('')
        timeLine = df.index
        close_data = df.values.transpose().tolist()
        return Response({"code": 20000,
                         'ts_code_list': companyCode,
                         'name_list': companyName,
                         'type_list': type,
                         'time_line': timeLine,
                         'close_data': close_data}, status=status.HTTP_200_OK)



class ItemHistData(generics.GenericAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [ authentication.BasicAuthentication ]

    def get(self, request, *args, **kwargs):
        if Company.objects.filter(ts_code=kwargs['ts_code']).exists():
            item = Company.objects.get(ts_code=kwargs['ts_code'])
            file_path = hist_data_path + item.ts_code + '.csv'
        elif Index.objects.filter(ts_code=kwargs['ts_code']).exists():
            item = Index.objects.get(ts_code=kwargs['ts_code'])
            file_path = index_hist_data_path + item.ts_code + '.csv'
        else:
            return Response({"code": 20004, "message": "item doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "item doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        condtions = {}
        if 'date__lte' in request.query_params:
            condtions['date__lte'] = request.query_params['date__lte'].replace("-", "")
        else:
            condtions['date__lte']= None

        if 'date__gte' in request.query_params:
            condtions['date__gte'] = request.query_params['date__gte'].replace("-", "")
        else:
            condtions['date__gte']= None

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})
        h_data.index = h_data['trade_date']

        h_data = h_data.loc[condtions['date__gte']: condtions['date__lte']]

        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'ts_code': item.ts_code, 'name': item.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)
