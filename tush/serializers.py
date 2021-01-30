from rest_framework import serializers
from tush.models import Company, Index, CompanyDailyBasic, IndexDailyBasic, CompanyDaily, IndexDaily, FundBasic, FundDaily, FundNav
from rest_framework.reverse import reverse
import os

index_hist_data_path = 'tushare_data/data/tush_index_hist_data/'


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
    def get_hist(self, instance):
        return reverse('index-hist-data', kwargs={'ts_code':instance.ts_code}, request=self.context['request'])

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


class CompanyDailyBasicSerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    name = serializers.SerializerMethodField('get_name')
    def get_hist(self, instance):
        return reverse('company-hist-data', kwargs={'ts_code':instance.ts_code}, request=self.context['request'])
    def get_name(self, instance):
        return Company.objects.get(ts_code=instance.ts_code).name

    def to_representation(self, instance):
        representation = super(CompanyDailyBasicSerializer, self).to_representation(instance)
        representation['trade_date'] = instance.trade_date.strftime('%Y-%m-%d') if instance.trade_date != None else ''
        return representation

    class Meta:
        model = CompanyDailyBasic
        fields = ('url', 'id', 'name',
                  "ts_code", "trade_date", "close", "turnover_rate", "turnover_rate_f",
                  "volume_ratio", "pe", "pe_ttm", "pb", "ps",
                  "ps_ttm", "total_share", "float_share", "free_share", "total_mv",
                  "circ_mv",
                  "hist_data"
                  )


class IndexDailyBasicSerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    name = serializers.SerializerMethodField('get_name')

    def get_hist(self, instance):
        return reverse('index-hist-data', kwargs={'ts_code': instance.ts_code}, request=self.context['request'])
    def get_name(self, instance):
        return Index.objects.get(ts_code=instance.ts_code).name

    class Meta:
        model = IndexDailyBasic
        fields = ('url', 'id', 'name',
                  "ts_code", "trade_date", "total_mv", "float_mv", "total_share",
                  "float_share", "free_share", "turnover_rate", "turnover_rate_f", "pe",
                  "pe_ttm", "pb",
                  "hist_data"
                  )


class CompanyDailySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    name = serializers.SerializerMethodField('get_name')
    def get_hist(self, instance):
        return reverse('company-hist-data', kwargs={'ts_code':instance.ts_code}, request=self.context['request'])
    def get_name(self, instance):
        return Company.objects.get(ts_code=instance.ts_code).name

    def to_representation(self, instance):
        representation = super(CompanyDailySerializer, self).to_representation(instance)
        representation['trade_date'] = instance.trade_date.strftime('%Y-%m-%d') if instance.trade_date != None else ''
        return representation

    class Meta:
        model = CompanyDaily
        fields = ('url', 'id', 'name',
                  "ts_code", "trade_date", "close", "open", "high",
                  "low", "pre_close", "change", "pct_chg", "vol",
                  "amount",
                  "hist_data"
                  )


class IndexDailySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    name = serializers.SerializerMethodField('get_name')

    def get_hist(self, instance):
        return reverse('index-hist-data', kwargs={'ts_code': instance.ts_code}, request=self.context['request'])
    def get_name(self, instance):
        return Index.objects.get(ts_code=instance.ts_code).name

    class Meta:
        model = IndexDaily
        fields = ('url', 'id', 'name',
                  "ts_code", "trade_date", "close", "open", "high",
                  "low", "pre_close", "change", "pct_chg", "vol",
                  "amount",
                  "hist_data"
                  )


class FundBasicSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = FundBasic
        fields = ('ts_code', 'name', 'management', 'custodian', 'fund_type',
              'found_date', 'due_date', 'list_date', 'issue_date', 'delist_date',
              'issue_amount', 'm_fee', 'c_fee', 'duration_year', 'p_value',
              'min_amount', 'exp_return', 'benchmark', 'status', 'invest_type',
              'type', 'trustee', 'purc_startdate', 'redm_startdate', 'market'
        )


class FundDailySerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.SerializerMethodField('get_name')

    def get_name(self, instance):
        try:
            return FundBasic.objects.get(ts_code=instance.ts_code).name
        except FundBasic.DoesNotExist:
            return ""

    class Meta:
        model = FundDaily
        fields = ('ts_code', 'name',
              'trade_date', 'open', 'high', 'low',
              'close', 'pre_close', 'change', 'pct_chg', 'vol',
              'amount'
        )


class FundNavSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.SerializerMethodField('get_name')

    def get_name(self, instance):
        try:
            return FundBasic.objects.get(ts_code=instance.ts_code).name
        except FundBasic.DoesNotExist:
            return ""

    class Meta:
        model = FundNav
        fields = ('ts_code', 'name',
              'ann_date', 'end_date', 'unit_nav', 'accum_nav',
              'accum_div', 'net_asset', 'total_netasset', 'adj_nav'
        )