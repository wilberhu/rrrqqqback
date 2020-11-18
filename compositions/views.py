from compositions.models import Composition
from compositions.serializers import CompositionSerializer
from rest_framework import generics

from util.permissions import IsOwnerOrReadOnly, IsObjectOwner

from rest_framework.reverse import reverse

from rest_framework import renderers, status
from rest_framework.response import Response

from django.http import HttpResponse
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

class CompositionList(generics.ListCreateAPIView):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):

        user = self.request.user
        filters = {}

        if not user.is_staff:
            filters["owner_id"] = user.id

        fields = self.serializer_class.Meta.fields
        if (self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return Composition.objects.filter(**filters)
        else:
            return Composition.objects.filter(**filters).order_by(self.request.query_params.get('sort'))

    def create(self, request, *args, **kwargs):
        print(json.loads(request.data["adjustments"]))
        print(request.data["adjustments"])

        return Response(json.loads(request.data["adjustments"]), status=status.HTTP_200_OK)


class CompositionDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = (IsObjectOwner,)

    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

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
        Composition.objects.filter(id=str(kwargs["pk"])).update(**param)
        strategy = Composition.objects.get(id=str(kwargs["pk"]))

        user = strategy.owner.username
        id = str(kwargs["pk"])
        py_folder = os.path.join("media/strategy", user, id)
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)

        res = run_algorithm(request, user, id, code)

        return Response(res, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
