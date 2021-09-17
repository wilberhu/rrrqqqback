from rest_framework import serializers
from tush.models import Company, Index, FundBasic

class CompanySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('url', 'symbol', 'ts_code', 'name',
                  'area', 'industry',  'fullname', 'enname', 'market',
                  'exchange', 'curr_type', 'list_status', 'list_date', 'delist_date',
                  'is_hs', 'has_his')

class CompanySimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Company
        fields = ('ts_code', 'name')


class IndexSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Index
        fields = ('url', 'ts_code', 'name', 'fullname',
                  'market', 'publisher',  'index_type', 'category', 'base_date',
                  'base_point', 'list_date', 'weight_rule', 'desc', 'exp_date',
                  'has_his')


class IndexSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Index
        fields = ('ts_code', 'name')


class FundBasicSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = FundBasic
        fields = ('ts_code', 'name', 'management', 'custodian', 'fund_type',
              'found_date', 'due_date', 'list_date', 'issue_date', 'delist_date',
              'issue_amount', 'm_fee', 'c_fee', 'duration_year', 'p_value',
              'min_amount', 'exp_return', 'benchmark', 'status', 'invest_type',
              'type', 'trustee', 'purc_startdate', 'redm_startdate', 'market',
              'has_his', 'has_nav', 'has_portfolio'
        )


class FundBasicSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FundBasic
        fields = ('ts_code', 'name')
