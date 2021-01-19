from rest_framework import serializers
from strategies.models import Strategy, FilterOption


class StrategySerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Strategy
        fields = ('url', 'id', 'owner', 'title', 'code',
                  'created', 'modified')


class FilterOptionSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = FilterOption
        fields = ('url', 'id', 'owner', 'key', 'label',
                  'table', 'method')
