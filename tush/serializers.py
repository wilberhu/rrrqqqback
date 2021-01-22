from rest_framework import serializers
from tush.models import Company, Index, CompanyDaily, IndexDaily, CompanyToday, IndexToday
from rest_framework.reverse import reverse
import os

index_hist_data_path = 'tushare_data/data/index_hist_data/'


class CompanySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    def get_hist(self, instance):
        return reverse('company-hist-data', kwargs={'ts_code':instance.ts_code}, request=self.context['request'])

    def to_representation(self, instance):
        representation = super(CompanySerializer, self).to_representation(instance)

        representation['url'] = reverse('company-detail', kwargs={'pk':instance.symbol}, request=self.context['request'])
        representation['list_date'] = instance.list_date.strftime('%Y-%m-%d') if instance.list_date != None else ''
        representation['delist_date'] = instance.delist_date.strftime('%Y-%m-%d') if instance.delist_date != None else ''

        return representation

    class Meta:
        model = Company
        fields = ('url', 'id', 'symbol', 'ts_code', 'name',
                  'area', 'industry',  'fullname', 'enname', 'market',
                  'exchange', 'curr_type', 'list_status', 'list_date', 'delist_date',
                  'is_hs', 'hist_data',)

class CompanySimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('ts_code', 'name')


class IndexSerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    def get_hist(self, index):
        return reverse('index-hist-data', kwargs={'ts_code':index.ts_code}, request=self.context['request'])

    has_hist_data = serializers.SerializerMethodField('get_has_hist')
    def get_has_hist(self, instance):

        file_path = index_hist_data_path + instance.ts_code + '.csv'
        if os.path.exists(file_path):
            return True
        else:
            return False

    def to_representation(self, instance):
        representation = super(IndexSerializer, self).to_representation(instance)

        representation['url'] = reverse('index-detail', kwargs={'pk':instance.ts_code}, request=self.context['request'])
        representation['base_date'] = instance.base_date.strftime('%Y-%m-%d') if instance.base_date != None else ''
        representation['list_date'] = instance.list_date.strftime('%Y-%m-%d') if instance.list_date != None else ''
        representation['exp_date'] = instance.exp_date.strftime('%Y-%m-%d') if instance.exp_date != None else ''

        return representation


    class Meta:
        model = Index
        fields = ('url', 'id', 'ts_code', 'name', 'fullname',
                  'market', 'publisher',  'index_type', 'category', 'base_date',
                  'base_point', 'list_date', 'weight_rule', 'desc', 'exp_date',
                  'hist_data', 'has_hist_data')


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