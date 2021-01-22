from stock_api.settings import MEDIA_ROOT, MEDIA_URL
from strategies.models import Strategy, FilterOption, StockPicking
from strategies.serializers import StrategySerializer, FilterOptionSerializer, StrategySimpleSerializer, \
    StockPickingSerializer
from rest_framework import generics

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import status, filters
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.db import connection

import os
import shutil
import re
import codecs

from strategies.run_algorithm import save_file
from back_test import factorFilter, strategyFilter


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


class FactorFilter(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = StrategySerializer

    def post(self,request,*args,**kwargs):
        params = request.data
        params["commission"]=int(request.data["commission"]) if "commission" in request.data else 0
        result=factorFilter.mainfunc(params)
        return Response(result, status=status.HTTP_200_OK)


class StrategyFilter(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = StrategySerializer

    def post(self,request,*args,**kwargs):
        params = request.data
        params["commission"]=int(request.data["commission"]) if "commission" in request.data else 0
        strategy = Strategy.objects.get(id=params['strategy'])
        strategy_import = "from " + MEDIA_URL.strip('/') + '.strategy.' + request.user.username + '.id' + str(strategy.id) + '.' + strategy.title + " import " + strategy.title
        params["strategy"] = strategy.title
        del params["name_list"]
        result=strategyFilter.mainfunc(strategy_import, **params)
        return Response(result, status=status.HTTP_200_OK)


class StockPickingList(generics.ListCreateAPIView):
    permission_classes = (IsOwnerOrReadOnly,)

    queryset = StockPicking.objects.all()
    serializer_class = StockPickingSerializer
    ordering_fields = '__all__'

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class StockPickingDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsObjectOwner,)

    queryset = StockPicking.objects.all()
    serializer_class = StockPickingSerializer

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)