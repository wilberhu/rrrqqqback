from rest_framework import serializers
from compositions.models import Composition

class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Composition
        fields = ('url', 'id', 'owner', 'adjustments', 'stock',
                  'benchmark', 'created')
