from rest_framework.authtoken.admin import User

from stock_api.settings import MEDIA_ROOT, MEDIA_URL
from strategies.models import Strategy, FilterOption, StockPicking, StockPickingResult
from strategies.serializers import StrategySerializer, FilterOptionSerializer, StrategySimpleSerializer, \
    StockPickingSerializer
from rest_framework import generics, authentication

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import status, filters
from rest_framework.response import Response
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection
from rest_framework.reverse import reverse
from django.forms.models import model_to_dict

import os
import shutil
import subprocess
import re
import json
import codecs
import pandas as pd

from strategies.run_algorithm import save_file
from ifund import factorFilter, strategyFilter


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
        save_file(request, user, id)

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

        save_file(self.request, user, id)

    def delete(self, request, *args, **kwargs):
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))
        py_folder = os.path.join(MEDIA_URL.strip('/'), "strategy", strategy.owner.username, "id"+str(kwargs["pk"]))
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)
        return self.destroy(request, *args, **kwargs)


class StrategyAllList(generics.ListAPIView):

    permission_classes = (IsOwnerOrReadOnly,)

    queryset = Strategy.objects.all().only('id', 'title')
    serializer_class = StrategySimpleSerializer

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
        'fold': os.path.join(MEDIA_URL.strip("/"), 'stock_picking', serializer.data['owner'], str(serializer.data.get('id')))
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
                    'activities': stock_picking_result['activities']
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
        print(res)

        result = StockPickingResult.objects.get(stock_picking_id=kwargs['pk'])
        if res['method'] == 'strategy':
            path = os.path.join(MEDIA_URL.strip("/"), result.path.split(MEDIA_URL.strip("/"))[-1].lstrip("/").rstrip('"'))
            df = pd.read_csv(path).fillna('')
            res['result'] = {
                'activities': json.loads(result.activities),
                'path': reverse('strategy-portfolio-download', args=[path]),

                'columns': df.columns,
                'group_data': {}
            }
            group_data = df.groupby(df['end_date'])
            for date, group in group_data:
                group['index'] = group.index
                res['result']['group_data'][date] = {
                    'results': group.to_dict('records'),
                    'count': group.shape[0]
                }
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
        elif request.data['method'] == 'factor':
            stock_picking_result = factor_filter(serializer, request)

        # 把结果集存进数据库
        stock_picking_result = StockPickingResult.objects.filter(stock_picking_id=serializer.data['id'])
        StockPickingResult.objects.update(**{
            'id': stock_picking_result.id,
            'stock_picking_id': serializer.data['id'],
            'activities': json.dumps(stock_picking_result['activities']),
            'path': stock_picking_result['path']
        })

        res = serializer.data
        res['result'] = {
            'activities': stock_picking_result['activities'],
            'path': stock_picking_result['path'],

            'columns': stock_picking_result['columns'],
            'group_data': stock_picking_result['group_data']
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