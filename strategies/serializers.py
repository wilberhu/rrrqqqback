from rest_framework import serializers
from strategies.models import Strategy, FilterOption, StockPicking
from rest_framework.fields import empty


class StrategySerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Strategy
        fields = ('url', 'id', 'owner', 'title', 'code',
                  'created', 'modified')


class StrategySimpleSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Strategy
        fields = ('id', 'title', 'owner')


class FilterOptionSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = FilterOption
        fields = ('url', 'id', 'owner', 'key', 'label',
                  'table', 'method')


class NullableJSONField(serializers.JSONField):

    def get_value(self, dictionary):
        result = super().get_value(dictionary)
        if result is empty:
            return []
        return result


class StockPickingSerializer(serializers.HyperlinkedModelSerializer):
    start_time = serializers.DateField(input_formats=['%Y%m%d'])
    end_time = serializers.DateField(input_formats=['%Y%m%d'])
    owner = serializers.ReadOnlyField(source='owner.username')
    filter = NullableJSONField(required=False)

    class Meta:
        model = StockPicking
        fields = ('url', 'id', 'name', 'description', 'owner',
                  'method', 'start_time', 'end_time', 'filter', 'created',
                  'modified')