from tush.models import Company, Index, CompanyDailyBasic, IndexDailyBasic, CompanyDaily, IndexDaily,\
    FundBasic, FundDaily, FundNav
from tush.serializers import CompanySerializer, CompanySimpleSerializer, IndexSerializer, IndexSimpleSerializer,\
    FundBasicSerializer, FundBasicSimpleSerializer
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

company_daily_path = 'tushare_data/data/tush_company_daily/'
index_daily_path = 'tushare_data/data/tush_index_daily/'
fund_daily_path = 'tushare_data/data/tush_fund_daily/'
fund_nav_path = 'tushare_data/data/tush_fund_nav/'
fund_portfolio_path = 'tushare_data/data/tush_fund_portfolio/'
# hist_data_length = -252*3
hist_data_length = 0

default_start = '19901219'


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


class CompanyQuery(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    def get_queryset(self):
        query_text = self.request.query_params.get('q')

        if query_text != None and query_text.strip() != '':
            return query_datasets('tush_company', self.serializer_class.Meta.fields, query_text)
        else:
            return []


class CompanyHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            company = Company.objects.get(ts_code=kwargs['ts_code'])
        except Company.DoesNotExist:
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        start = request.query_params.get('start') if request.query_params.get('start') != None else default_start
        end = request.query_params.get('end')
        trade_date = request.query_params.get('trade_date')

        hist_data = query_stock_hist_data('tush_companydaily', kwargs['ts_code'], trade_date, start, end)
        return Response({"code": 20000, 'ts_code': company.ts_code, 'name': company.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)


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


class IndexQuery(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = IndexSimpleSerializer

    def get_queryset(self):
        query_text = self.request.query_params.get('q')

        if query_text != None and query_text.strip() != '':
            return query_datasets('tush_index', self.serializer_class.Meta.fields, query_text)
        else:
            return []


class IndexHistData(generics.GenericAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CompanySimpleSerializer

    authentication_classes = [ authentication.BasicAuthentication ]

    def get(self, request, *args, **kwargs):
        try:
            index = Index.objects.get(ts_code=kwargs['ts_code'])
        except Index.DoesNotExist:
            return Response({"code": 20004, "message": "index doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        start = request.query_params.get('start') if request.query_params.get('start') != None else default_start
        end = request.query_params.get('end')
        trade_date = request.query_params.get('trade_date')

        hist_data = query_stock_hist_data('tush_indexdaily', kwargs['ts_code'], trade_date, start, end)
        return Response({"code": 20000, 'ts_code': index.ts_code, 'name': index.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)


class CompanyDailyList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol',
                  'amount']
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_companydaily', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_company')
        return Response(res, status=status.HTTP_200_OK)


class IndexDailyList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = self.request.query_params.get('limit')
        offset = self.request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol',
                  'amount']
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_indexdaily', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_index')
        return Response(res, status=status.HTTP_200_OK)


class CompanyDailyBasicList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ["ts_code", "trade_date", "close", "turnover_rate", "turnover_rate_f",
                  "volume_ratio", "pe", "pe_ttm", "pb", "ps",
                  "ps_ttm", "total_share", "float_share", "free_share", "total_mv",
                  "circ_mv"]
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_companydailybasic', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_company')
        return Response(res, status=status.HTTP_200_OK)


class IndexDailyBasicList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ["ts_code", "trade_date", "total_mv", "float_mv", "total_share",
                  "float_share", "free_share", "turnover_rate", "turnover_rate_f", "pe",
                  "pe_ttm", "pb"]
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_indexdailybasic', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_index')
        return Response(res, status=status.HTTP_200_OK)


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

        if len(ts_code_list_request) <= 0 or len(ts_code_list_request) > 20:
            response['detail'] = "The companies should be more than 0 and less than 20."
            return Response(response, status=status.HTTP_200_OK)

        conditions = {}
        conditions['date__lte'] = request.query_params.get('date__lte').replace("-", "") if request.query_params.get('date__lte') != None else None
        conditions['date__gte'] = request.query_params.get('date__gte').replace("-", "") if request.query_params.get('date__gte') != None else None
        
        close_data_list = []
        for index, code in enumerate(ts_code_list_request):
            if type_list_request[index] == 'company':
                company = Company.objects.get(ts_code=code)
                file_path = company_daily_path + company.ts_code + '.csv'
                tmp_type = 'company'
            elif type_list_request[index] == 'index':
                company = Index.objects.get(ts_code=code)
                file_path = index_daily_path + company.ts_code + '.csv'
                tmp_type = 'index'
            elif type_list_request[index] == 'fund':
                company = FundBasic.objects.get(ts_code=code)
                file_path = fund_nav_path + company.ts_code + '.csv'
                tmp_type = 'fund'
            else:
                continue

            if not os.path.exists(file_path):
                continue

            response['ts_code_list'].append(company.ts_code)
            response['name_list'].append(company.name)
            response['type_list'].append(tmp_type)

            if type_list_request[index] == 'fund':
                column = 'unit_nav'
                h_data = pd.read_csv(file_path, dtype={column: float})[['nav_date', column]]
                h_data.dropna(axis=0, how='any')
                h_data.drop_duplicates(subset=['nav_date'], inplace=True)
                h_data.index = h_data['nav_date']
            else:
                column = 'close'
                h_data = pd.read_csv(file_path, dtype={column: float})[['trade_date', column]]
                h_data.dropna(axis=0, how='any')
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


class FundDailyList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ['ts_code', 'trade_date', 'open', 'high', 'low',
                  'close', 'pre_close', 'change', 'pct_chg', 'vol',
                  'amount']
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_funddaily', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_fundbasic')
        return Response(res, status=status.HTTP_200_OK)


class FundNavList(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        limit = int(limit) if limit != None else 10
        offset = int(offset) if offset != None else 0

        sort_by = None
        descending = None
        if self.request.query_params.get('ordering') != None:
            sort_by = self.request.query_params.get('ordering').lstrip('-')
            descending = self.request.query_params.get('ordering').startswith('-')

        fields = ['ts_code', 'ann_date', 'nav_date', 'unit_nav', 'accum_nav',
                  'accum_div', 'net_asset', 'total_netasset', 'adj_nav']
        conditions = []
        for field in fields:
            if request.query_params.get(field) != None:
                conditions.append({
                    'name': field,
                    'value': request.query_params.get(field)
                })

        res = get_datasets('tush_fundnav', ['*'], conditions=conditions, limit=limit, offset=offset, sort_by=sort_by, descending=descending, table_for_name='tush_fundbasic', key_date="nav_date")
        return Response(res, status=status.HTTP_200_OK)


class FundBasicQuery(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = FundBasicSimpleSerializer

    def get_queryset(self):
        query_text = self.request.query_params.get('q')
        market = self.request.query_params.get('market')

        if query_text != None and query_text.strip() != '':
            return query_datasets('tush_fundbasic', self.serializer_class.Meta.fields, query_text, filter={'market':market})
        else:
            return []


class FundBasicHistData(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        try:
            fund = FundBasic.objects.get(ts_code=kwargs['ts_code'])
        except Company.DoesNotExist:
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        file_path = fund_daily_path + fund.ts_code + '.csv'
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "company doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        h_data = pd.read_csv(file_path, dtype={"trade_date": str}).fillna('')

        h_data = h_data[hist_data_length::]
        hist_data = np.array(h_data[['trade_date', 'open', 'close', 'low', 'high']]).tolist()
        # ma_data = np.around(np.array(h_data[['ma5', 'ma10', 'ma20']]).transpose(), decimals=2).tolist()
        return Response({"code": 20000, 'ts_code': fund.ts_code, 'name': fund.name, 'hist_data': hist_data}, status=status.HTTP_200_OK)


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
                file_path = company_daily_path + company.ts_code + '.csv'
                tmp_type = 'company'
            elif type_list_request[index] == 'index':
                company = Index.objects.get(ts_code=code)
                file_path = index_daily_path + company.ts_code + '.csv'
                tmp_type = 'index'
            elif type_list_request[index] == 'fund':
                company = FundBasic.objects.get(ts_code=code)
                file_path = fund_nav_path + company.ts_code + '.csv'
                tmp_type = 'fund'
            else:
                continue

            if not os.path.exists(file_path):
                continue

            response['ts_code_list'].append(company.ts_code)
            response['name_list'].append(company.name)
            response['type_list'].append(tmp_type)

            h_data = pd.read_csv(file_path, dtype={column: float})[['nav_date', column]]

            h_data.index = h_data['nav_date']
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
        file_path = os.path.join(fund_portfolio_path, kwargs['ts_code'] + '.csv')
        if not os.path.exists(file_path):
            return Response({}, status=status.HTTP_200_OK)

        df = pd.read_csv(file_path).fillna('')
        group_data = df.groupby(df['end_date'])
        res = {}

        end_date = int(request.query_params.get('end_date')) if 'end_date' in request.query_params and int(request.query_params.get('end_date')) in group_data.keys.tolist() else \
            group_data.keys.tolist()[-1]

        for date, group in group_data:
            if end_date == date:
                group['index'] = group.index
                res[date] = {
                    'results': group.to_dict('records'),
                    'count': group.shape[0]
                }
            else:
                res[date] = {
                    'results': [],
                    'count': 0
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


################################## custom function ##################################
def query_datasets(table, fields, query_text, filter={}):
    cursor = connection.cursor()

    fields_str = ", ".join(fields)
    select_str = 'select {} from {}'.format(fields_str, table)

    where_conditions = []
    for field in fields:
        where_conditions.append(field + " like '%" + query_text + "%'")
    where_conditions_str = ' where (' + ' or '.join(where_conditions) + ')'

    filter_conditions = []
    for key in filter.keys():
        if filter[key] != None:
            filter_conditions.append(key + "='" + filter[key] + "'")
    filter_conditions_str = ' and ' +  ' and '.join(filter_conditions) if len(filter_conditions) > 0 else ''

    limit_str = ' limit 0, 10'

    sql = select_str + where_conditions_str + filter_conditions_str + limit_str

    print(sql)
    cursor.execute(sql)
    return [
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()
    ]


def get_datasets(table, fields=['*'], conditions=[], limit=10, offset=0, sort_by=None, descending=None, table_for_name=None, key_date="trade_date"):
    cursor = connection.cursor()

    select_str = "select {} from {}".format(", ".join(fields), table)

    where_conditions = []
    where_conditions.append("{}=(select max({}) from {})".format(key_date, key_date, table))
    for condition in conditions:
        where_conditions.append("{}='{}'".format(condition['name'], condition['value']))
    where_conditions_str = " where " + " and ".join(where_conditions)

    order_str = ""
    if sort_by != None:
        order_str += " ORDER BY {} ".format(sort_by)
        if descending == True:
            order_str += " DESC "
        elif descending == False:
            order_str += " ASC "

    limit_condition_str = ' limit ' + str(offset) + ', ' + str(limit)

    sql = select_str + where_conditions_str + order_str + limit_condition_str
    print(sql)

    # 查询列表
    cursor.execute(sql)
    results = [
        dict(zip([col[0] for col in cursor.description], row))
        for row in cursor.fetchall()
    ]

    # 查询name
    if table_for_name != None and len(results)>0:
        select_for_name = "select ts_code,name from {}".format(table_for_name)
        where_conditions_str_for_name = " where ts_code in ({})".format(",".join(["'"+item['ts_code']+"'" for item in results]))
        sql_for_name = select_for_name + where_conditions_str_for_name
        cursor.execute(sql_for_name)
        name_dict = {}
        for row in cursor.fetchall():
            name_dict[row[0]] = row[1]
        for i in range(len(results)):
            results[i]['name'] = name_dict[results[i]['ts_code']] if results[i]['ts_code'] in name_dict else None

    select_str_count = "select count(*) from {}".format(table)
    sql_count = select_str_count + where_conditions_str

    # 统计个数
    cursor.execute(sql_count)
    count = int(cursor.fetchone()[0])

    cursor.close()
    return {
        'results': results,
        'count': count
    }

def query_stock_hist_data(table_name, ts_code, trade_date, start, end):
    cursor = connection.cursor()
    sql = "select trade_date, open, close, low, high, `change`, pct_chg, amount from {} where ts_code='{}' and close IS NOT null".format(table_name, ts_code)

    additional_condition = ''

    if trade_date:
        additional_condition = " and datediff(cast('{}' as datetime),trade_date)=0".format(trade_date)
    elif start and end:
        additional_condition = " and trade_date between cast('{}' as datetime) and cast('{}' as datetime)".format(start,
                                                                                                                  end)
    elif start:
        additional_condition = " and datediff(cast('{}' as datetime),trade_date)<0".format(start)
    elif end:
        additional_condition = " and datediff(cast('{}' as datetime),trade_date)>0".format(end)

    sql += additional_condition
    sql += " order by trade_date"
    print(sql)

    cursor.execute(sql)
    hist_data = [
        [row[0].strftime('%Y%m%d')] + list(row[1:])
        for row in cursor.fetchall()
    ]

    cursor.close()
    return hist_data