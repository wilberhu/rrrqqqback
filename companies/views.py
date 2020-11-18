from companies.models import Company, Index
from companies.serializers import CompanySerializer, CompanyCloseSerializer, IndexSerializer
from rest_framework import generics, status

from util.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from django.db import connection
import pandas as pd
import numpy as np
import os
import re
import django_filters.rest_framework

hist_data_path = 'tushare_data/data/hist_data/'
index_hist_data_path = 'tushare_data/data/index_hist_data/'
# hist_data_length = -780
hist_data_length = 0

# class CompanyList(generics.ListCreateAPIView):
class CompanyList(generics.ListAPIView):
    serializer_class = CompanySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('symbol', 'ts_code', 'name')
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if (self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return Company.objects.all()
        else:
            return Company.objects.all().order_by(self.request.query_params.get('sort'))


# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class CompanyDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    def get_object(self):
        symbol = "%06d" % (int(self.kwargs['pk']))
        if not Company.objects.filter(symbol=symbol).exists():
            return None
        return Company.objects.get(symbol=symbol)

class CompanyHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):

        # 正则判断是否是数值
        value = re.compile(r'^[-+]?[0-9]+$')
        isdigit = value.match(kwargs['symbol'])

        if isdigit:
            symbol = "%06d" % (int(kwargs['symbol']))
        else:
            symbol = kwargs['symbol']

        if not Company.objects.filter(symbol=symbol).exists():
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        company = Company.objects.get(symbol=symbol)

        file_path = hist_data_path + company.ts_code + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'company_code': company.ts_code, 'company_name': company.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)

# class Company_Market_All(generics.GenericAPIView):
#
#     permission_classes = (IsOwnerOrReadOnly)
#     queryset = Company.objects.all()
#
#     def get(self, request, *args, **kwargs):
#
#         cursor = connection.cursor()
#         cursor.execute('select code, name from models_markettoday')
#         rows = cursor.fetchall()  # 读取所有
#         results = []
#         for row in rows:
#             results.append({
#                 'code': row[0],
#                 'name': row[1]
#             })
#
#         cursor.execute('select code, name from companies_company')
#         rows = cursor.fetchall()  # 读取所有
#         for row in rows:
#             results.append({
#                 'code': row[0],
#                 'name': row[1]
#             })
#         cursor.close()
#         # return results
#         return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)
#
#
# class Company_Market_Query(generics.GenericAPIView):
#     serializer_class = CompanyCloseSerializer
#
#     def post(self, request, *args, **kwargs):
#         if 'code' not in request.data:
#             return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)
#
#         if not isinstance(eval(request.data['code'].strip()), int):
#             return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)
#         code = int(request.data['code'])
#
#         cursor = connection.cursor()
#         cursor.execute('select code, name from models_markettoday')
#         rows = cursor.fetchall()  # 读取所有
#         results = []
#         for row in rows:
#             results.append({
#                 'code': row[0],
#                 'name': row[1]
#             })
#
#         cursor.execute('select code, name from companies_company')
#         rows = cursor.fetchall()  # 读取所有
#         for row in rows:
#             results.append({
#                 'code': row[0],
#                 'name': row[1]
#             })
#         # return results
#         cursor.close()
#         return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)


class IndexList(generics.ListAPIView):
    serializer_class = IndexSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('ts_code', 'name')
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if (self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return Index.objects.all()
        else:
            return Index.objects.all().order_by(self.request.query_params.get('sort'))


# class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
class IndexDetail(generics.RetrieveAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Index.objects.all()
    serializer_class = IndexSerializer

    def get_object(self):
        ts_code = self.kwargs['pk']
        if not Index.objects.filter(ts_code=ts_code).exists():
            return None
        return Index.objects.get(ts_code=ts_code)

class IndexHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        if not Index.objects.filter(ts_code=kwargs['ts_code']).exists():
            return Response({"code": 20004, "message": "index doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        index = Index.objects.get(ts_code=kwargs['ts_code'])

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
    serializer_class = CompanyCloseSerializer

    def post(self, request, *args, **kwargs):
        close_data_list = []
        companyCode = []
        companyName = []
        type = []

        if 'ts_code' not in request.data:
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        codes = re.split("[\n,; ]", request.data['ts_code'])
        print(codes)
        if len(codes) <= 0 or len(codes) > 10:
            return Response({"code": 20000,
                             'company_code': companyCode,
                             'company_name': companyName,
                             'type': type,
                             'time_line': [],
                             'close_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

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

            h_data = pd.read_csv(file_path)[['trade_date', 'close']]
            h_data.index = h_data['trade_date']
            h_data = h_data['close']
            close_data_list.append(h_data[hist_data_length::])
        if len(close_data_list) == 0:
            return Response({"code": 20000,
                             'company_code': companyCode,
                             'company_name': companyName,
                             'type': type,
                             'time_line': [],
                             'close_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

        print(close_data_list)
        df = pd.concat(close_data_list, axis=1).fillna('')
        timeLine = df.index
        close_data = df.values.transpose().tolist()
        return Response({"code": 20000,
                         'company_code': companyCode,
                         'company_name': companyName,
                         'type': type,
                         'time_line': timeLine,
                         'close_data': close_data}, status=status.HTTP_200_OK)



class ItemHistData(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get(self, request, *args, **kwargs):
        # 正则判断是否是数值
        value = re.compile(r'^[-+]?[0-9]+$')
        if 'pk' not in request.query_params or request.query_params['pk'].strip == '':
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        elif value.match(request.query_params.get('pk')):
            code = "%06d" % (int(request.query_params.get('pk')))
        else:
            code = request.query_params.get('pk')


        if Company.objects.filter(symbol=code).exists():
            item = Company.objects.get(symbol=code)
            file_path = hist_data_path + item.ts_code + '.csv'
        elif Company.objects.filter(ts_code=code).exists():
            item = Company.objects.get(ts_code=code)
            file_path = hist_data_path + item.ts_code + '.csv'
        elif Index.objects.filter(ts_code=code).exists():
            item = Index.objects.get(ts_code=code)
            file_path = index_hist_data_path + item.ts_code + '.csv'
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "index doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str})

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'item_code': item.ts_code, 'item_name': item.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)

class ItemDetail(generics.RetrieveAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get(self, request, *args, **kwargs):
        # 正则判断是否是数值
        value = re.compile(r'^[-+]?[0-9]+$')
        if 'pk' not in request.query_params or request.query_params['pk'].strip == '':
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        elif value.match(request.query_params.get('pk')):
            code = "%06d" % (int(request.query_params.get('pk')))
        else:
            code = request.query_params.get('pk')

        if Company.objects.filter(symbol=code).exists():
            return Response(CompanySerializer(Company.objects.get(symbol=code), context={'request': request}).data, status=status.HTTP_200_OK)
        elif Company.objects.filter(ts_code=code).exists():
            return Response(CompanySerializer(Company.objects.get(ts_code=code), context={'request': request}).data, status=status.HTTP_200_OK)
        elif Index.objects.filter(ts_code=code).exists():
            return Response(IndexSerializer(Index.objects.get(ts_code=code), context={'request': request}).data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


