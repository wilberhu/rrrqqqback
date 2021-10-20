from rest_framework import serializers
from strategies.models import Strategy, StockFilter
from rest_framework.fields import empty


class StrategySerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Strategy
        fields = ('url', 'id', 'owner', 'title', 'code',
                  'created', 'modified')


class StockFilterSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    submit_time = serializers.DateTimeField(required=False, allow_null=True)
    result_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = StockFilter
        fields = ('url', 'id', 'type', 'owner', 'title', 'code',
                  'name_cn', 'description', 'created', 'modified', 'submit_time', 'result_id')


class NullableJSONField(serializers.JSONField):

    def get_value(self, dictionary):
        result = super().get_value(dictionary)
        if result is empty:
            return []
        return result
