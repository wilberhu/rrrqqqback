from stock_api.settings import MEDIA_ROOT, MEDIA_URL
from django.contrib.auth.models import User
from rest_framework import serializers
from datasets.models import Dataset
import os

strategy_path = 'strategy_filter'

class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # file = serializers.FileField(required=True, allow_empty_file=False)
    highlight = serializers.HyperlinkedIdentityField(view_name='dataset-highlight', format='html')

    def to_representation(self, instance):
        representation = super(DatasetSerializer, self).to_representation(instance)
        representation['path'] = representation['file'].split(os.path.join(MEDIA_URL.strip('/'), strategy_path, representation['owner']) + '/', 2)[1]
        if instance.file.size < 1024:
            representation['size'] = str(instance.file.size) + "B"
        elif 1024 <= instance.file.size < 1024*1024:
            representation['size'] = str(round(instance.file.size/1024, 2)) + "KB"
        else:
            representation['size'] = str(round(instance.file.size / 1024 / 1024, 2)) + "MB"
        return representation

    class Meta:
        model = Dataset
        fields = ('url', 'id', 'name', 'owner', 'file', 'path', 'created', 'highlight')
