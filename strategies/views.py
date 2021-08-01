from rest_framework.authtoken.admin import User

from stock_api.settings import MEDIA_ROOT, MEDIA_URL
from strategies.models import Strategy, FilterOption, StockPicking, StockPickingResult, StockFilter, StockFilterResult
from strategies.serializers import StrategySerializer, FilterOptionSerializer, StrategySimpleSerializer, \
    StockPickingSerializer, StockFilterSerializer, StockFilterSimpleSerializer
from rest_framework import generics, authentication
from tush.models import Company, Index, CompanyDailyBasic, IndexDailyBasic, CompanyDaily, IndexDaily,\
    FundBasic, FundDaily, FundNav

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import status, filters
from rest_framework.response import Response
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from rest_framework.reverse import reverse
from django.forms.models import model_to_dict

import os
import sys
import shutil
import subprocess
import re
import json
import datetime
import codecs
import pandas as pd
import importlib

from strategies.run_algorithm import save_file
from ifund import factorFilter, strategyFilter, formatResult, dailyTraderFund

hist_data_path = 'tushare_data/data/tush_hist_data/'
index_hist_data_path = 'tushare_data/data/tush_index_hist_data/'
fund_hist_data_path = 'tushare_data/data/tush_fund_hist_data/'
fund_nav_data_path = 'tushare_data/data/tush_fund_nav_data/'
fund_portfolio_path = 'tushare_data/data/tush_fund_portfolio/'


class StrategyList(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    permission_classes = (IsOwnerOrReadOnly,)
    ordering_fields = '__all__'

    def create(self, request, *args, **kwargs):
        title = re.sub('[^a-zA-Z0-9_]','',self.request.data["title"].strip().replace(" ", ""))

        if "title" not in request.data or title == "" or \
                "code" not in request.data or request.data["code"] == "":
            response = {}
            response["error"] = True
            response["detail"] = "title or code cannot be null"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        param = {
            "code": "",
            "title": title
        }
        # 保存请求数据
        serializer.save(owner=self.request.user, **param)

        user = self.request.user.username
        id = str(serializer.data["id"])
        save_file(request, 'strategy', user, id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StrategyDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def perform_update(self, serializer):
        title = re.sub('[^a-zA-Z0-9_]', '', self.request.data["title"].strip().replace(" ", "_"))
        code = self.request.data["code"]
        param = {
            "code": "",
            "title": title
        }
        # 保存请求数据
        serializer.save(owner=self.request.user, **param)
        user = self.request.user.username
        id = str(serializer.data['id'])
        py_folder = os.path.join(MEDIA_URL.strip('/'), "strategy", user, "id" + id)
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)

        save_file(self.request, 'strategy', user, id)

    def delete(self, request, *args, **kwargs):
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))
        py_folder = os.path.join(MEDIA_URL.strip('/'), "strategy", strategy.owner.username, "id"+str(kwargs["pk"]))
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)
        return self.destroy(request, *args, **kwargs)


class StrategyCode(generics.GenericAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        strategy = self.get_object()
        py_folder = os.path.join(MEDIA_URL.strip('/'), "strategy", strategy.owner.username, "id"+str(kwargs["pk"]))
        f = codecs.open(os.path.join(py_folder, str(strategy.title) + ".py"), 'r', 'utf-8')
        code = f.read()
        f.close()
        return Response(code)


class StrategyParam(generics.GenericAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        strategy = self.get_object()

        strategy_import_package = MEDIA_URL.strip('/') + '.strategy.' + strategy.owner.username + '.id' + str(kwargs["pk"]) + '.' + strategy.title
        exec("import " + strategy_import_package)
        try:
            code_eval = compile(strategy_import_package + ".param", '<string>', 'eval')
            result = eval(code_eval)
        except:
            result = {}

        sys.modules.pop(strategy_import_package)
        return Response(result)


class StrategyAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Strategy.objects.all().only('id', 'title')
    serializer_class = StrategySimpleSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['id', 'title']
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']

    pagination_class = None

def import_code(code, name):
    # create blank module
    module_spec = importlib.machinery.ModuleSpec(name, None)
    module = importlib.util.module_from_spec(module_spec)
    # populate the module with code
    exec(code, module.__dict__)
    return module

class StockFilterList(generics.ListCreateAPIView):
    queryset = StockFilter.objects.all()
    serializer_class = StockFilterSerializer

    permission_classes = (IsOwnerOrReadOnly,)
    ordering_fields = '__all__'

    def create(self, request, *args, **kwargs):
        title = re.sub('[^a-zA-Z0-9_]','',self.request.data["title"].strip().replace(" ", ""))

        if "title" not in request.data or title == "" or \
                "code" not in request.data or request.data["code"] == "":
            response = {}
            response["error"] = True
            response["detail"] = "title or code cannot be null"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        m = import_code(request.data["code"], 'StockFilter')

        key = "name_cn"
        s = re.findall(r"@" + key + ":(.+?)\n", m.__doc__) if m.__doc__ != None else ""
        name_cn = s[0].strip() if s.__len__() > 0 else ''

        key = "description"
        s = re.findall(r"@" + key + ":(.+?)\n", m.__doc__) if m.__doc__ != None else ""
        description = s[0].strip() if s.__len__() > 0 else ''

        param = {
            "code": "",
            "title": title,
            "name_cn": name_cn,
            "description": description
        }
        # 保存请求数据
        serializer.save(owner=self.request.user, **param)

        user = self.request.user.username
        id = str(serializer.data["id"])
        save_file(request, "stock_filter", user, id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StockFilterDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = StockFilter.objects.all()
    serializer_class = StockFilterSerializer

    def perform_update(self, serializer):
        title = re.sub('[^a-zA-Z0-9_]', '', self.request.data["title"].strip().replace(" ", "_"))
        code = self.request.data["code"]

        m = import_code(code, 'test')

        key = "name_cn"
        s = re.findall(r"@" + key + ":(.+?)\n", m.__doc__)
        name_cn = s[0].strip() if s.__len__() > 0 else ''

        key = "description"
        s = re.findall(r"@" + key + ":(.+?)\n", m.__doc__)
        description = s[0].strip() if s.__len__() > 0 else ''

        param = {
            "code": "",
            "title": title,
            "name_cn": name_cn,
            "description": description
        }
        # 保存请求数据
        serializer.save(owner=self.request.user, **param)
        user = self.request.user.username
        id = str(serializer.data['id'])
        py_folder = os.path.join(MEDIA_URL.strip('/'), "stock_filter", user, "id" + id)

        # if os.path.exists(py_folder):
        #     shutil.rmtree(py_folder)

        save_file(self.request, "stock_filter", user, id)

    def delete(self, request, *args, **kwargs):
        stock_filter = StockFilter.objects.get(id=str(kwargs["pk"]))
        py_folder = os.path.join(MEDIA_URL.strip('/'), "stock_filter", stock_filter.owner.username, "id"+str(kwargs["pk"]))
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)
        return self.destroy(request, *args, **kwargs)



class StockFilterCode(generics.GenericAPIView):
    queryset = StockFilter.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        stock_filter = self.get_object()
        py_folder = os.path.join(MEDIA_URL.strip('/'), "stock_filter", stock_filter.owner.username, "id"+str(kwargs["pk"]))
        f = codecs.open(os.path.join(py_folder, str(stock_filter.title) + ".py"), 'r', 'utf-8')
        code = f.read()
        f.close()
        return Response(code)


class StockFilterData(generics.GenericAPIView):
    queryset = StockFilter.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        if((not StockFilter.objects.filter(id=kwargs['pk']).exists()) or
                StockFilter.objects.get(id=kwargs['pk']).result_id == None or
                request.query_params.get('force_update') == 'yes'):
            stock_filter = StockFilter.objects.get(id=kwargs['pk'])
            strategy = self.get_object()

            strategy_import_package = MEDIA_URL.strip('/') + '.stock_filter.' + strategy.owner.username + '.id' + str(kwargs["pk"]) + '.' + strategy.title
            exec("from " + strategy_import_package + " import main")
            code_eval = compile("main()", '<string>', 'eval')
            df = eval(code_eval)

            sys.modules.pop(strategy_import_package)

            csv_path = MEDIA_URL.strip('/') + '/stock_filter/' + strategy.owner.username + '/id' + str(kwargs["pk"]) + '/' + strategy.title + '.csv'
            df.to_csv(csv_path)

            # 存储结果集
            defaults = {
                'path': csv_path,
                'stock_filter_id': stock_filter.id
            }
            kwargs_result = {
                'id': stock_filter.result_id
            }
            StockFilterResult.objects.update_or_create(defaults, **kwargs_result)
            stock_filter_result = StockFilterResult.objects.filter(stock_filter_id=stock_filter.id)

            # 存储请求参数
            defaults = {
                'submit_time': datetime.datetime.now(),
                'result_id': stock_filter_result[0].id
            }
            kwargs_result = {
                'id': stock_filter.id
            }
            StockFilter.objects.update_or_create(defaults, **kwargs_result)

        else:
            stock_filter_result = StockFilterResult.objects.get(id=StockFilter.objects.get(id=kwargs['pk']).result_id)
            df = pd.read_csv(stock_filter_result.path).fillna("")

        limit = int(request.query_params.get('limit'))
        offset = int(request.query_params.get('offset'))
        if request.query_params.get('ordering') != None:
            sort_by = request.query_params.get('ordering').lstrip('-')
            descending = request.query_params.get('ordering').startswith('-')
            try:
                df = df.sort_values(by=sort_by, ascending=not descending)
            except:
                df[sort_by] = df[sort_by].apply(lambda x: str(x))
                df = df.sort_values(by=sort_by, ascending=not descending)
        result = {
            "results": df.iloc[offset:offset+limit].to_dict('records'),
            "columns": df.columns,
            "count": df.shape[0]
        }

        return Response(result)


class StockFilterAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = StockFilter.objects.all().only('id', 'title', 'code', 'name_cn', 'description')
    serializer_class = StockFilterSimpleSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['id', 'title']
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']

    pagination_class = None


class FilterOptionList(generics.ListCreateAPIView):
    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionSerializer

    permission_classes = (IsOwnerOrReadOnly,)
    ordering_fields = '__all__'

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FilterOptionDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionSerializer


class FilterOptionAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'

    pagination_class = None


class SqlQuery(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    def post(self, request, *args, **kwargs):
        cursor = connection.cursor()
        cursor.execute('select * from companies_company')
        # row = cursor.fetchone()  # 返回结果行游标直读向前，读取一条
        rows = cursor.fetchall()  # 读取所有
        results = []
        for row in rows:
            print(row)

        cursor.close()
        return Response({"rows": rows}, status=status.HTTP_200_OK)


def factor_filter(serializer, request):
        params = request.data
        params["commission"]=float(request.data["commission"]) if "commission" in request.data else 0
        return factorFilter.mainfunc(params['filter'])


def strategy_filter(serializer, request):
    res = {
        'group_data': {},
        'path': '',
        'columns': [],
        'activities': []
    }
    if 'strategy' not in serializer.data.get('filter'):
        return Response(res, status=status.HTTP_200_OK)

    strategy = Strategy.objects.get(id=serializer.data.get('filter')['strategy'])
    strategy_import = "from " + MEDIA_URL.strip('/') + '.strategy.' + serializer.data['owner'] + '.id' + str(strategy.id) + '.' + strategy.title + " import main"
    exec(strategy_import)

    params = {
        'startTime': serializer.data.get('filter')['startTime'],
        'endTime': serializer.data.get('filter')['endTime'],
        'allfund': serializer.data.get('filter')['allfund'],
        'commission': serializer.data.get('filter')['commission'],
        'fold': os.path.join(MEDIA_URL.strip("/"), 'stock_picking', serializer.data['owner'], str(serializer.data.get('id'))),
        'param': serializer.data.get('filter')['param']
    }

    # 创建文件夹
    if os.path.exists(params['fold']):
        shutil.rmtree(params['fold'])
    os.makedirs(params['fold'])

    # 运行策略
    code_eval = compile("main(**params)", '<string>', 'eval')
    result = eval(code_eval)

    return strategyFilter.calculateShare(result, params)


class StockPickingList(generics.ListCreateAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    queryset = StockPicking.objects.all()
    serializer_class = StockPickingSerializer
    ordering_fields = '__all__'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)

        if request.data['method'] == 'strategy':
            stock_picking_result = strategy_filter(serializer, request)
            # 把结果集存进数据库
            StockPickingResult.objects.create(**{
                'stock_picking_id': serializer.data['id'],
                'activities': json.dumps(stock_picking_result['activities']),
                'path': stock_picking_result['path']
            })

            res = {
                'id': serializer.data['id'],
                'result': {
                    'activities': stock_picking_result['activities'],
                    'path': stock_picking_result['path'],

                    'columns': stock_picking_result['columns'],
                    'group_data': stock_picking_result['group_data']
                }
            }
        elif request.data['method'] == 'factor':
            stock_picking_result = factor_filter(serializer, request)
            # 把结果集存进数据库
            StockPickingResult.objects.create(**{
                'stock_picking_id': serializer.data['id'],
                'activities': json.dumps(stock_picking_result['activities'])
            })

            res = {
                'id': serializer.data['id'],
                'result': {
                    'activities': stock_picking_result['activities'],
                    'group_data': {}
                }
            }
        return Response(res, status=status.HTTP_200_OK)



class StockPickingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsObjectOwner,)

    queryset = StockPicking.objects.all()
    serializer_class = StockPickingSerializer


    def get(self, request, *args, **kwargs):
        stock_picking = StockPicking.objects.get(id=kwargs['pk'])
        res = model_to_dict(stock_picking)

        result = StockPickingResult.objects.get(stock_picking_id=kwargs['pk'])
        if res['method'] == 'strategy':

            result = {
                'activities': json.loads(result.activities),
                'path': os.path.join(MEDIA_URL.strip("/"), result.path.split(MEDIA_URL.strip("/"))[-1].lstrip("/").rstrip('"')),
            }
            res['result'] = formatResult.formatResult(result)
        elif res['method'] == 'factor':
            res['result'] = {
                'activities': json.loads(result.activities),
                'group_data': {}
            }
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        stock_picking = StockPicking.objects.get(id=kwargs['pk'])

        serializer = self.get_serializer(stock_picking, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(id=stock_picking.id, owner=stock_picking.owner)

        if request.data['method'] == 'strategy':
            stock_picking_result = strategy_filter(serializer, request)

            # 把结果集存进数据库
            stock_picking_result_id = StockPickingResult.objects.get(stock_picking_id=serializer.data['id']).id
            StockPickingResult.objects.filter(stock_picking_id=serializer.data['id']).update(**{
                'id': stock_picking_result_id,
                'stock_picking_id': serializer.data['id'],
                'activities': json.dumps(stock_picking_result['activities']),
                'path': stock_picking_result['path'] if 'path' in stock_picking_result else None
            })

            res = serializer.data
            res['result'] = formatResult.formatResult(stock_picking_result)
        elif request.data['method'] == 'factor':
            stock_picking_result = factor_filter(serializer, request)

            # 把结果集存进数据库
            stock_picking_result_id = StockPickingResult.objects.get(stock_picking_id=serializer.data['id']).id
            StockPickingResult.objects.filter(stock_picking_id=serializer.data['id']).update(**{
                'id': stock_picking_result_id,
                'stock_picking_id': serializer.data['id'],
                'activities': json.dumps(stock_picking_result['activities']),
            })

            res = {
                'id': serializer.data['id'],
                'result': {
                    'activities': stock_picking_result['activities'],
                    'group_data': {}
                }
            }

        return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        queryset = self.retrieve(request, *args, **kwargs)
        path = os.path.join(MEDIA_URL.strip("/"), 'stock_picking', queryset.data['owner'], kwargs['pk'])
        if os.path.exists(path):
            shutil.rmtree(path)
        return self.destroy(request, *args, **kwargs)


class StrategyPortfolioDownloadList(generics.ListAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = StrategySerializer

    authentication_classes = [authentication.BasicAuthentication]
    queryset = Strategy.objects.all()

    def get(self, request, *args, **kwargs):
        file_path = kwargs['path']
        if not os.path.exists(file_path):
            return Response({"code": 20004, "message": "fund '" + kwargs['ts_code'] + "' portfolio doesn't exists"}, status=status.HTTP_404_NOT_FOUND)

        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename="' + file_path.split('/')[-1] + '"'
            return response


class CompositionData(generics.GenericAPIView):
    # def get(self, request, *args, **kwargs):
    #     return Response({"detail": "Method \"GET\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = StrategySerializer

    authentication_classes = [authentication.BasicAuthentication]

    def post(self, request, *args, **kwargs):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~ start: ", datetime.datetime.now())
        ts_code_list = request.data.get('ts_code_list')
        timestamp = request.data.get('timestamp').replace("-", "")
        allfund = request.data.get('allfund')
        commission = request.data.get('commission')
        activities = dailyTraderFund.calculate_fund_share(ts_code_list, timestamp, allfund, commission)

        data = {
            "allfund": allfund,
            "commission": commission,
            "activities": activities
        }
        result = dailyTraderFund.composition_calculate(data)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~ end: ", datetime.datetime.now())
        return Response(result, status=status.HTTP_201_CREATED)