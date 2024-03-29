from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from strategies import views
from django.conf.urls import include

urlpatterns = format_suffix_patterns([

    url(r'^api-auth/',
        include('rest_framework.urls')),

    url(r'^strategies/$',
        views.StrategyList.as_view(),
        name='strategy-list'),
    url(r'^strategies/(?P<pk>[0-9]+)/$',
        views.StrategyDetail.as_view(),
        name='strategy-detail'),
    url(r'^strategies/(?P<pk>[0-9]+)/code/$',
        views.StrategyCode.as_view(),
        name='strategy-code'),
    url(r'^strategies/all/$',
        views.StrategyAllList.as_view(),
        name='strategy-list-all'),

    url(r'^stock_filters/$',
        views.StockFilterList.as_view(),
        name='stockfilter-list'),
    url(r'^stock_filters/(?P<pk>[0-9]+)/$',
        views.StockFilterDetail.as_view(),
        name='stockfilter-detail'),
    url(r'^stock_filters/(?P<pk>[0-9]+)/code/$',
        views.StockFilterCode.as_view(),
        name='stockfilter-code'),
    url(r'^stock_filters/(?P<pk>[0-9]+)/data/$',
        views.StockFilterData.as_view(),
        name='stockfilter-data'),
    url(r'^stock_filters/all/$',
        views.StockFilterAllList.as_view(),
        name='stockfilter-list-all'),

    url(r'^combine/(?P<column>[\w.]+)/$',
        views.CompositionData.as_view(),
        name='close-data'),
])