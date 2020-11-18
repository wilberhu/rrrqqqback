from rest_framework import serializers
from strategies.models import Strategy, Results, LANGUAGE_CHOICES, STYLE_CHOICES

from django.contrib.auth.models import User

class StrategySerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='strategy-highlight', format='html')
    resulturl = serializers.HyperlinkedIdentityField(view_name='strategy-result-url', format='html')

    start_date = serializers.DateField(format="%Y-%m-%d")
    end_date = serializers.DateField(format="%Y-%m-%d")

    def to_representation(self, instance):
        representation = super(StrategySerializer, self).to_representation(instance)
        if Results.objects.filter(strategy_id=instance.id).exists():
            result = Results.objects.get(strategy_id=instance.id)
            representation['Total_Returns'] = result.Total_Returns
            representation['Annual_Returns'] = result.Annual_Returns
        return representation


    class Meta:
        model = Strategy
        fields = ('url', 'id', 'highlight', 'owner',
                  'title', 'code', 'start_date', 'end_date', 'stock',
                  'benchmark', 'created', 'resulturl')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='strategy-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')


class StrategyCompareSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Strategy
        fields = ('id', 'code')