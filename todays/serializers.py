from rest_framework import serializers
from todays.models import CompanyToday
from todays.models import IndexToday
from rest_framework.reverse import reverse
from companies.models import Company, Index

import os

index_hist_data_path = 'tushare_data/data/index_hist_data/'

class CompanyTodaySerializer(serializers.HyperlinkedModelSerializer):


    hist_data = serializers.SerializerMethodField('get_hist')
    def get_hist(self, company):
        return reverse('company-hist-data', kwargs={'ts_code':company.ts_code}, request=self.context['request'])

    def to_representation(self, instance):
        representation = super(CompanyTodaySerializer, self).to_representation(instance)
        company = Company.objects.get(ts_code=instance.ts_code)
        representation['name'] = company.name
        representation['trade_date'] = instance.trade_date.strftime('%Y-%m-%d') if instance.trade_date != None else ''
        return representation

    class Meta:
        model = CompanyToday
        fields = ('url', 'id',
                  "ts_code", "trade_date", "close", "open", "high",
                  "low", "pre_close", "change", "pct_chg", "vol",
                  "amount",
                  "hist_data"
                  )


class IndexTodaySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')

    def get_hist(self, company):
        return reverse('index-hist-data', kwargs={'ts_code': company.ts_code}, request=self.context['request'])

    def to_representation(self, instance):
        representation = super(IndexTodaySerializer, self).to_representation(instance)
        company = Index.objects.get(ts_code=instance.ts_code)
        representation['name'] = company.name
        return representation

    class Meta:
        model = IndexToday
        fields = ('url', 'id',
                  "ts_code", "trade_date", "close", "open", "high",
                  "low", "pre_close", "change", "pct_chg", "vol",
                  "amount",
                  "hist_data"
                  )