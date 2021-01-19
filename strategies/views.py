from strategies.models import Strategy, FilterOption
from strategies.serializers import StrategySerializer, FilterOptionSerializer
from rest_framework import generics

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework import status
from rest_framework.response import Response

from django.db import connection

import os
import shutil
import re
import codecs

from strategies.run_algorithm import save_file
from back_test import stockFilter


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

    def put(self, request, *args, **kwargs):
        title = re.sub('[^a-zA-Z0-9_]','',self.request.data["title"].strip().replace(" ", "_"))
        if "title" not in request.data or title == "" or \
                "code" not in request.data or request.data["code"] == "":
            response = {}
            response["error"] = True
            response["detail"] = "title or code cannot be null"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = self.request.data["code"]
        param = {
            "code": "",
            "title": title
        }
        Strategy.objects.filter(id=str(kwargs["pk"])).update(**param)
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))

        user = strategy.owner.username
        id = str(kwargs["pk"])
        py_folder = os.path.join("media/strategy", user, id)
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)

        save_file(request, user, id)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        strategy = Strategy.objects.get(id=str(kwargs["pk"]))
        py_folder = os.path.join("media/strategy", strategy.owner.username, str(kwargs["pk"]))
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)
        return self.destroy(request, *args, **kwargs)


class FilterOptionList(generics.ListCreateAPIView):
    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionSerializer

    permission_classes = (IsOwnerOrReadOnly,)
    ordering_fields = '__all__'
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FilterOptionDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = FilterOption.objects.all()
    serializer_class = FilterOptionSerializer


class StrategyCode(generics.GenericAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsObjectOwner,)

    def get(self, request, *args, **kwargs):
        strategy = self.get_object()
        py_folder = os.path.join("media/strategy", strategy.owner.username, str(kwargs["pk"]))
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


class StrategyFilter(generics.ListCreateAPIView):
    queryset = Strategy.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = StrategySerializer

    def post(self,request,*args,**kwargs):
        params = request.data
        params["commission"]=int(request.data["commission"]) if "commission" in request.data else 0
        result=stockFilter.mainfunc(params)
        print(result)
        return Response(result, status=status.HTTP_200_OK)