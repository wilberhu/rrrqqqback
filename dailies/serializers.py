from rest_framework import serializers
from dailies.models import CompanyDaily
from dailies.models import IndexDaily
from rest_framework.reverse import reverse
from companies.models import Company, Index

import os

index_hist_data_path = 'tushare_data/data/index_hist_data/'

class CompanyDailySerializer(serializers.HyperlinkedModelSerializer):


    hist_data = serializers.SerializerMethodField('get_hist')
    def get_hist(self, company):
        return reverse('company-hist-data', kwargs={'ts_code':company.ts_code}, request=self.context['request'])

    def to_representation(self, instance):
        representation = super(CompanyDailySerializer, self).to_representation(instance)
        company = Company.objects.get(ts_code=instance.ts_code)
        representation['name'] = company.name
        representation['trade_date'] = instance.trade_date.strftime('%Y-%m-%d') if instance.trade_date != None else ''
        return representation

    class Meta:
        model = CompanyDaily
        fields = ('url', 'id',
                  "ts_code", "trade_date", "close", "turnover_rate", "turnover_rate_f",
                  "volume_ratio", "pe", "pe_ttm", "pb", "ps",
                  "ps_ttm", "total_share", "float_share", "free_share", "total_mv",
                  "circ_mv",
                  "hist_data"
                  )


class IndexDailySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')

    def get_hist(self, company):
        return reverse('index-hist-data', kwargs={'ts_code': company.ts_code}, request=self.context['request'])

    def to_representation(self, instance):
        representation = super(IndexDailySerializer, self).to_representation(instance)
        company = Index.objects.get(ts_code=instance.ts_code)
        representation['name'] = company.name
        return representation

    class Meta:
        model = IndexDaily
        fields = ('url', 'id',
                  "ts_code", "trade_date", "total_mv", "float_mv", "total_share",
                  "float_share", "free_share", "turnover_rate", "turnover_rate_f", "pe",
                  "pe_ttm", "pb",
                  "hist_data"
                  )