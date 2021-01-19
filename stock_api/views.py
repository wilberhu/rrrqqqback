from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'datasets': reverse('dataset-list', request=request, format=format),
        'strategies': reverse('strategy-list', request=request, format=format),
        'filter_options': reverse('filter-option-list', request=request, format=format),
        'compositions': reverse('composition-list', request=request, format=format),
        'compositions_calculate': reverse('composition-calculate', request=request, format=format),
        'companies': reverse('company-list', request=request, format=format),
        'indexes': reverse('index-list', request=request, format=format),
        'companies_daily': reverse('companydaily-list', request=request, format=format),
        'indexes_daily': reverse('indexdaily-list', request=request, format=format),
        'companies_today': reverse('companytoday-list', request=request, format=format),
        'indexes_today': reverse('indextoday-list', request=request, format=format),
        'data': reverse('close-data', request=request, args=['close'], format=format),
        'item-hist-data': reverse('item-hist-data', request=request, kwargs={'ts_code': "000001.SZ"}, format=format),
        'strategy-filter': reverse('strategy-filter', request=request, format=format),

    })
