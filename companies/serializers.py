from rest_framework import serializers
from companies.models import Company, Index
from rest_framework.reverse import reverse
import os

index_hist_data_path = 'tushare_data/data/index_hist_data/'


class CompanySerializer(serializers.HyperlinkedModelSerializer):

    hist_data = serializers.SerializerMethodField('get_hist')
    def get_hist(self, instance):
        return reverse('company-hist-data', kwargs={'symbol':instance.symbol}, request=self.context['request'])

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


class CompanyCloseSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'ts_code')


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
