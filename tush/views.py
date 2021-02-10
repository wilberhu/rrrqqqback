from tush.models import Company, Index, CompanyDailyBasic, IndexDailyBasic, CompanyDaily, IndexDaily,\
    FundBasic, FundDaily, FundNav
from tush.serializers import CompanySerializer, CompanySimpleSerializer, IndexSerializer,\
    CompanyDailyBasicSerializer, IndexDailyBasicSerializer, CompanyDailySerializer, IndexDailySerializer,\
    FundBasicSerializer, FundDailySerializer, FundNavSerializer
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework import authentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from django.http import HttpResponse

from util.permissions import IsOwnerOrReadOnly

from django.db import connection
from django.core import serializers
import pandas as pd
import numpy as np
import os
import re
import datetime
import django_filters.rest_framework

hist_data_path = 'tushare_data/data/tush_hist_data/'
index_hist_data_path = 'tushare_data/data/tush_index_hist_data/'
fund_hist_data_path = 'tushare_data/data/tush_fund_hist_data/'
fund_nav_data_path = 'tushare_data/data/tush_fund_nav_data/'
fund_portfolio_path = 'tushare_data/data/tush_fund_portfolio/'
# hist_data_length = -780
hist_data_length = 0


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
            print(kwargs['ts_code'])
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


class CompanyDailyBasicList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDailyBasic.objects.all()
    serializer_class = CompanyDailyBasicSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class CompanyDailyBasicDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDailyBasic.objects.all()
    serializer_class = CompanyDailyBasicSerializer


class IndexDailyBasicList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDailyBasic.objects.all()
    serializer_class = IndexDailyBasicSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class IndexDailyBasicDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDailyBasic.objects.all()
    serializer_class = IndexDailyBasicSerializer


class CompanyDailyList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDaily.objects.all()
    serializer_class = CompanyDailySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class CompanyDailyDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = CompanyDaily.objects.all()
    serializer_class = CompanyDailySerializer


class IndexDailyList(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']
    search_fields = ['ts_code']
    ordering_fields = '__all__'


class IndexDailyDetail(generics.RetrieveAPIView):

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    queryset = IndexDaily.objects.all()
    serializer_class = IndexDailySerializer


class CloseData(generics.GenericAPIView):
    # def get(self, request, *args, **kwargs):
    #     return Response({"detail": "Method \"GET\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [ authentication.BasicAuthentication ]

    def post(self, request, *args, **kwargs):
        column = kwargs['column']  # open || close || unit_nav

        response = {
            'code': 20000,
            'ts_code_list': [],
            'name_list': [],
            'type_list': [],
            'time_line': [],
            'close_data': [],
            'detail': ''
        }

        if 'ts_code_list' not in request.data:
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        ts_code_list_request = request.data['ts_code_list']
        type_list_request = request.data['type_list']

        if len(ts_code_list_request) <= 0 or len(ts_code_list_request) > 10:
            response['detail'] = "The companies should be more than 0 and less than 10."
            return Response(response, status=status.HTTP_200_OK)

        conditions = {}
        conditions['date__lte'] = request.query_params.get('date__lte').replace("-", "") if request.query_params.get('date__lte') != None else None
        conditions['date__gte'] = request.query_params.get('date__gte').replace("-", "") if request.query_params.get('date__gte') != None else None
        
        close_data_list = []
        for index, code in enumerate(ts_code_list_request):
            if type_list_request[index] == 'company':
                company = Company.objects.get(ts_code=code)
                file_path = hist_data_path + company.ts_code + '.csv'
                tmp_type = 'company'
            elif type_list_request[index] == 'index':
                company = Index.objects.get(ts_code=code)
                file_path = index_hist_data_path + company.ts_code + '.csv'
                tmp_type = 'index'
            elif type_list_request[index] == 'fund':
                company = FundBasic.objects.get(ts_code=code)
                file_path = fund_nav_data_path + company.ts_code + '.csv'
                tmp_type = 'fund'
            else:
                continue

            if not os.path.exists(file_path):
                continue

            response['ts_code_list'].append(company.ts_code)
            response['name_list'].append(company.name)
            response['type_list'].append(tmp_type)

            h_data = pd.read_csv(file_path, dtype={column: float})[['trade_date', column]]
            h_data.index = h_data['trade_date']
            h_data = h_data[column]

            h_data = h_data.loc[conditions['date__gte']: conditions['date__lte']]

            close_data_list.append(h_data)
        if len(response['ts_code_list']) == 0:
            response['detail'] = "The companies should be more than 0 and less than 10."
            return Response(response, status=status.HTTP_200_OK)

        df = pd.concat(close_data_list, axis=1).fillna('')
        response['time_line'] = df.index
        response['close_data'] = df.values.transpose().tolist()
        return Response(response, status=status.HTTP_200_OK)


class FundBasicList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundBasic.objects.all()
    serializer_class = FundBasicSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name']

    search_fields = ['ts_code', 'name']
    ordering_fields = '__all__'


class FundBasicDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundBasic.objects.all()
    serializer_class = FundBasicSerializer

    def get_object(self):
        symbol = self.kwargs['pk']
        return FundBasic.objects.filter(symbol=symbol).first()


class FundDailyList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundDaily.objects.all()
    serializer_class = FundDailySerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']

    search_fields = ['ts_code']
    ordering_fields = '__all__'


class FundDailyDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundDaily.objects.all()
    serializer_class = FundDailySerializer

    def get_object(self):
        symbol = self.kwargs['pk']
        return FundDaily.objects.filter(symbol=symbol).first()


class FundNavList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundNav.objects.all()
    serializer_class = FundNavSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code']

    search_fields = ['ts_code']
    ordering_fields = '__all__'

class FundBasicAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundBasic.objects.all().only('ts_code', 'name', 'market')
    serializer_class = CompanySimpleSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['ts_code', 'name', 'market']
    search_fields = ['ts_code', 'name']
    ordering_fields = ['ts_code', 'name']

    pagination_class = None



class FundNavDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FundNav.objects.all()
    serializer_class = FundNavSerializer

    def get_object(self):
        symbol = self.kwargs['pk']
        return FundNav.objects.filter(symbol=symbol).first()


class FundBasicHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            print(kwargs['ts_code'])
            fund = FundBasic.objects.get(ts_code=kwargs['ts_code'])
        except Company.DoesNotExist:
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        file_path = fund_hist_data_path + fund.ts_code + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'company_code': fund.ts_code, 'company_name': fund.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)


class FundNavData(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [authentication.BasicAuthentication]

    def post(self, request, *args, **kwargs):
        column = kwargs['column']  # open || close || unit_nav

        response = {
            'code': 20000,
            'ts_code_list': [],
            'name_list': [],
            'type_list': [],
            'time_line': [],
            'close_data': [],
            'detail': ''
        }

        if 'ts_code_list' not in request.data:
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        ts_code_list_request = request.data['ts_code_list']
        type_list_request = request.data['type_list']

        if len(ts_code_list_request) <= 0 or len(ts_code_list_request) > 10:
            response['detail'] = "The companies should be more than 0 and less than 10."
            return Response(response, status=status.HTTP_200_OK)

        conditions = {}
        conditions['date__lte'] = request.query_params.get('date__lte').replace("-", "") if request.query_params.get('date__lte') != None else None
        conditions['date__gte'] = request.query_params.get('date__gte').replace("-", "") if request.query_params.get('date__gte') != None else None

        close_data_list = []
        for index, code in enumerate(ts_code_list_request):
            if type_list_request[index] == 'company':
                company = Company.objects.get(ts_code=code)
                file_path = hist_data_path + company.ts_code + '.csv'
                tmp_type = 'company'
            elif type_list_request[index] == 'index':
                company = Index.objects.get(ts_code=code)
                file_path = index_hist_data_path + company.ts_code + '.csv'
                tmp_type = 'index'
            elif type_list_request[index] == 'fund':
                company = FundBasic.objects.get(ts_code=code)
                file_path = fund_nav_data_path + company.ts_code + '.csv'
                tmp_type = 'fund'
            else:
                continue

            if not os.path.exists(file_path):
                continue

            response['ts_code_list'].append(company.ts_code)
            response['name_list'].append(company.name)
            response['type_list'].append(tmp_type)

            h_data = pd.read_csv(file_path, dtype={column: float})[['end_date', column]]

            h_data.index = h_data['end_date']
            h_data = h_data[column]

            h_data = h_data.loc[conditions['date__gte']: conditions['date__lte']]

            close_data_list.append(h_data)

        if len(response['ts_code_list']) == 0:
            response['detail'] = "The companies should be more than 0 and less than 10."
            return Response(response, status=status.HTTP_200_OK)

        df = pd.concat(close_data_list, axis=1).fillna('')
        response['time_line'] = df.index
        response['close_data'] = df.values.transpose().tolist()
        return Response(response, status=status.HTTP_200_OK)


class FundPortfolioList(generics.ListAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [authentication.BasicAuthentication]
    queryset = FundBasic.objects.all()

    def get(self, request, *args, **kwargs):
        file_path = fund_portfolio_path + kwargs['ts_code'] + '.csv'
        if not os.path.exists(file_path):
            res = {
                'results': [],
                'count': 0
            }
            return Response(res, status=status.HTTP_200_OK)

        offset = int(request.query_params.get("offset")) if request.query_params.get("offset") else 0
        limit = int(request.query_params.get("limit")) if request.query_params.get("limit") else 100
        df = pd.read_csv(file_path).fillna('')
        df['index'] = df.index
        res = {
            'results': df.to_dict('records')[offset:offset+limit],
            'count': df.shape[0]
        }
        return Response(res, status=status.HTTP_200_OK)


class FundPortfolioDownloadList(generics.ListAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [authentication.BasicAuthentication]
    queryset = FundBasic.objects.all()

    def get(self, request, *args, **kwargs):
        file_path = fund_portfolio_path + kwargs['ts_code'] + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "fund '" + kwargs['ts_code'] + "' portfolio doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename="portfolio_' + kwargs['ts_code'] + '.csv' + '"'
            return response
