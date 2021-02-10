import shutil

from rest_framework.response import Response

from datasets.models import Dataset
from datasets.serializers import DatasetSerializer
from rest_framework import generics, status
from util.permissions import IsOwnerOrReadOnly, IsObjectOwner
import os

from django.http import HttpResponse

class datasetList(generics.ListCreateAPIView):
    # queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        filters = {}

        if not user.is_staff:
            filters["owner_id"] = user.id

        fields = self.serializer_class.Meta.fields
        if (self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return Dataset.objects.filter(**filters)
        else:
            return Dataset.objects.filter(**filters).order_by(self.request.query_params.get('sort'))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.data["path"] = request.data['file'].split("media/strategy/" + request.data['owner'] + "/", 1)[1]
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class datasetDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    permission_classes = (IsObjectOwner,)

    def delete(self, request, *args, **kwargs):
        dataset = self.retrieve(request, *args, **kwargs)

        shutil.rmtree(os.path.join("media/strategy", dataset.data['owner'], "datasets", dataset.data['path'].split("/")[1]))
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        dataset = self.retrieve(request, *args, **kwargs)
        shutil.rmtree(os.path.join("media/strategy", dataset.data['owner'], "datasets", dataset.data['path'].split("/")[1]))
        return self.update(request, *args, **kwargs)


class datasetDelete(generics.GenericAPIView):
    permission_classes = (IsOwnerOrReadOnly,)
    def delete(self, request, *args, **kwargs):
        ids = request.data['ids'].split(",")
        delete = []
        for id in ids:
            if Dataset.objects.filter(id=id).exists():
                dataset = Dataset.objects.get(id=int(id))
                print(dataset.file.name)
                dataset_random_code = dataset.file.name.split("strategy/" + dataset.owner.username + "/datasets/", 1)[1].split("/")[0]
                shutil.rmtree(os.path.join("media/strategy", dataset.owner.username, "datasets", dataset_random_code))
                dataset.delete()
                delete.append(id)
        return Response({"delete": delete, "detail": "deleted " + str(delete)}, status=status.HTTP_200_OK)

class datasetHighlight(generics.GenericAPIView):
    permission_classes = (IsObjectOwner,)

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def get(self, request, *args, **kwargs):
        dataset = self.get_object()
        filename = dataset.file.name.split(os.path.join("strategy", request.user.username, "datasets"), 1)[1].split("/", 2)[2]

        with open(os.path.join("media", dataset.file.name), "rb") as f:
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
            return response
        # return Response(dataset.file)