from strategies.models import Strategy, Results
from strategies.serializers import StrategySerializer, StrategyCompareSerializer
from rest_framework import generics

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import renderers, status
from rest_framework.response import Response

from django.http import HttpResponse
from django.db import connection
from PIL import Image

from strategies.run_algorithm import run_algorithm
import os
import json
import shutil
from django.core import serializers
import pandas as pd
import numpy as np
import re
import codecs
from back_test import strategyTools

class StrategyList(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):

        user = self.request.user
        filters = {}

        if not user.is_staff:
            filters["owner_id"] = user.id

        fields = self.serializer_class.Meta.fields
        if (self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return Strategy.objects.filter(**filters)
        else:
            return Strategy.objects.filter(**filters).order_by(self.request.query_params.get('sort'))

    def create(self, request, *args, **kwargs):
        '''
        title = re.sub('[^a-zA-Z0-9_]','',self.request.data["title"].strip().replace(" ", "_"))

        if "title" not in request.data or title == "" or \
                "code" not in request.data or request.data["code"] == "":
            response = {}
            response["error"] = True
            response["detail"] = "title or code cannot be null"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = self.request.data["code"]
        param = {
            "code": "",
            "title": title,
            "start_date": self.request.data["start_date"],
            "end_date": self.request.data["end_date"],
            "stock": self.request.data["stock"],
            "benchmark": self.request.data["benchmark"]
        }
        # 保存请求数据
        serializer.save(owner=self.request.user, **param)

        user = self.request.user.username
        id = str(serializer.data["id"])
        '''
        stock=request.data["code"]
        start_date=request.data["start"]
        end_data=request.data["end"]
        cash=request.data["cash"]
        if "comm" not in request.data:
            comm = 0
        else: 
            comm=request.data["comm"]
        celue=request.data["strategy"]

        print(stock,start_date,end_data,cash,comm,celue)
        res = strategyTools.basic(stock, start_date, end_data, cash, comm, celue)

        return Response([res], status=status.HTTP_200_OK)


class StrategyDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def put(self, request, *args, **kwargs):
        title = re.sub('[^a-zA-Z0-9_]','',self.request.data["title"].strip().replace(" ", "_"))
        if "title" not in request.data or title == "" or \
                "code" not in request.data or request.data["code"] == "":
            response = {}
            response["error"] = True
            response["detail"] = "title or code cannot be null"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = self.request.data["code"]
        param = {
            "code": "",
            "title": title,
            "start_date": self.request.data["start_date"],
            "end_date": self.request.data["end_date"],
            "stock": self.request.data["stock"],
            "benchmark": self.request.data["benchmark"]
        }
        Strategy.objects.filter(id=str(kwargs["pk"])).update(**param)
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))

        user = strategy.owner.username
        id = str(kwargs["pk"])
        py_folder = os.path.join("media/strategy", user, id)
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)

        res = run_algorithm(request, user, id, code)

        return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))
        py_folder = os.path.join("media/strategy", strategy.owner.username, str(kwargs["pk"]))
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)
        return self.destroy(request, *args, **kwargs)


class ImageUrl(generics.GenericAPIView):
    queryset = Strategy.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        try:
            strategy = Strategy.objects.get(id=str(kwargs["pk"]))
            py_folder = os.path.join("media/strategy", strategy.owner.username, str(kwargs["pk"]))
            with open(os.path.join(py_folder, "result.jpg"), "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except IOError:
            red = Image.new('RGB', (32, 32), (255, 255, 255))
            # response = HttpResponse(content_type="application/force-download")
            response = HttpResponse(content_type="image/jpeg")
            red.save(response, "JPEG")
            return response

class StrategyHighlight(generics.GenericAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsObjectOwner,)

    renderer_classes = (renderers.StaticHTMLRenderer,)

    # def get(self, request, *args, **kwargs):
    #     strategy = self.get_object()
    #     return Response(strategy.highlighted)

    def get(self, request, *args, **kwargs):
        strategy = self.get_object()
        py_folder = os.path.join("media/strategy", strategy.owner.username, str(kwargs["pk"]))
        f = codecs.open(os.path.join(py_folder, str(strategy.title) + ".py"), 'r', 'utf-8')
        code = f.read()
        f.close()
        return Response(code)

class ResultUrl(generics.RetrieveAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        res = {}
        if Results.objects.filter(strategy_id=int(kwargs["pk"])).exists():
            result = Results.objects.get(strategy_id=int(kwargs["pk"]))
            data = serializers.serialize('json', [result,])
            res = json.loads(data)[0]["fields"]
            # res['image'] = reverse('strategy-image-url', args=[kwargs["pk"]], request=request)

            strategy = Strategy.objects.get(id=str(kwargs["pk"]))
            user = strategy.owner.username
            py_folder = os.path.join("media/strategy", user, kwargs["pk"])
            result = pd.read_csv(os.path.join(py_folder, "result.csv")).fillna("")
            res["result"] = {}
            res["result"]["date"] = result["date"]
            res["result"]["portfolio"] = result["portfolio"]
            res["result"]["benchmark_portfolio"] = result["benchmark_portfolio"]
            res["result"]["daily_returns"] = result["daily_returns"]

            result_trade = pd.read_csv(os.path.join(py_folder, "result_trade.csv")).fillna("")
            result_side = pd.read_csv(os.path.join(py_folder, "result_side.csv")).fillna("")

            res["result"]["params_index"] = ["portfolio", "benchmark_portfolio",
                                             "daily_returns"] + result_trade.columns.tolist()[:-1]

            res["result"]["amount"] = np.transpose(result_trade[result_trade.columns.tolist()[:-1]].values)
            res["result"]["side"] = np.transpose(result_side[result_side.columns.tolist()[:-1]].values)
        return Response(res, status=status.HTTP_200_OK)


class StrategyCompare(generics.GenericAPIView):
    permission_classes = (IsObjectOwner,)
    serializer_class = StrategyCompareSerializer

    def post(self, request, *args, **kwargs):
        strategy_data_list = []
        strategyIds = []
        strategyTitles = []

        if 'code' not in request.data:
            return Response({"detail": "The required fields is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        strategy_ids = re.split("[\n,; ]", request.data['code'])
        print(strategy_ids)
        if len(strategy_ids) <= 0 or len(strategy_ids) > 10:
            return Response({"code": 20000,
                             'strategy_ids': strategyIds,
                             'strategy_titles': strategyTitles,
                             'time_line': [],
                             'strategy_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

        for strategy_id in strategy_ids:
            strategy_id = strategy_id.strip()
            if strategy_id == "":
                continue
            elif Strategy.objects.filter(id=strategy_id).exists():
                strategy = Strategy.objects.get(id=strategy_id)
                file_path = os.path.join("media/strategy", strategy.owner.username, strategy_id, "result.csv")
            else:
                continue

            if not os.path.exists(file_path):
                continue

            strategyIds.append(strategy_id)
            strategyTitles.append(strategy.title)

            h_data = pd.read_csv(file_path)[['date', 'portfolio']]
            h_data.index = h_data['date']
            h_data = h_data['portfolio']
            strategy_data_list.append(h_data)
        if len(strategy_data_list) == 0:
            return Response({"code": 20000,
                             'strategy_ids': strategyIds,
                             'strategy_titles': strategyTitles,
                             'time_line': [],
                             'strategy_data': [],
                             'detail': "The companies should be more than 0 and less than 10."},
                            status=status.HTTP_200_OK)

        df = pd.concat(strategy_data_list, axis=1).fillna('')
        timeLine = df.index
        strategy_data = df.values.transpose().tolist()
        return Response({"code": 20000,
                         'strategy_ids': strategyIds,
                         'strategy_titles': strategyTitles,
                         'time_line': timeLine,
                         'strategy_data': strategy_data}, status=status.HTTP_200_OK)


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
        return Response({"columns": "123"}, status=status.HTTP_200_OK)
