from rest_framework import serializers
from compositions.models import Composition
from rest_framework.fields import empty


class NullableJSONField(serializers.JSONField):

    def get_value(self, dictionary):
        result = super().get_value(dictionary)
        if result is empty:
            return []
        return result


class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    activities = NullableJSONField(required=False)

    class Meta:
        model = Composition
        fields = ('url', 'id', 'name', 'description', 'owner',
                  'allfund', 'comission', 'activities', 'created', 'modified')
