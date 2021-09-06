from rest_framework import serializers
from tush.models import Company, Index, CompanyDailyBasic, IndexDailyBasic, CompanyDaily, IndexDaily, FundBasic, FundDaily, FundNav
from rest_framework.reverse import reverse
import os

index_hist_data_path = 'tushare_data/data/tush_index_daily/'
fund_hist_data_path = 'tushare_data/data/tush_fund_daily/'
fund_portfolio_path = 'tushare_data/data/tush_fund_portfolio/'


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
        fields = ('url', 'symbol', 'ts_code', 'name',
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
        fields = ('url', 'ts_code', 'name', 'fullname',
                  'market', 'publisher',  'index_type', 'category', 'base_date',
                  'base_point', 'list_date', 'weight_rule', 'desc', 'exp_date',
                  'hist_data', 'has_hist_data')


class IndexSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Index
        fields = ('ts_code', 'name')


class FundBasicSerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    has_hist_data = serializers.SerializerMethodField('get_has_hist')
    portfolio = serializers.SerializerMethodField('get_portfolio')
    has_portfolio = serializers.SerializerMethodField('get_has_portfolio')

    def get_hist(self, instance):
        return reverse('fundbasic-hist-data', kwargs={'ts_code': instance.ts_code}, request=self.context['request'])

    def get_has_hist(self, instance):
        file_path = fund_hist_data_path + instance.ts_code + '.csv'
        if os.path.exists(file_path):
            return True
        else:
            return False

    def get_portfolio(self, instance):
        return reverse('fundbasic-portfolio', kwargs={'ts_code': instance.ts_code}, request=self.context['request'])
    def get_has_portfolio(self, instance):
        file_path = fund_portfolio_path + instance.ts_code + '.csv'
        if os.path.exists(file_path):
            return True
        else:
            return False

    class Meta:
        model = FundBasic
        fields = ('ts_code', 'name', 'management', 'custodian', 'fund_type',
              'found_date', 'due_date', 'list_date', 'issue_date', 'delist_date',
              'issue_amount', 'm_fee', 'c_fee', 'duration_year', 'p_value',
              'min_amount', 'exp_return', 'benchmark', 'status', 'invest_type',
              'type', 'trustee', 'purc_startdate', 'redm_startdate', 'market',
              'has_hist_data', 'hist_data', 'has_portfolio', 'portfolio'
        )


class FundBasicSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FundBasic
        fields = ('ts_code', 'name')
