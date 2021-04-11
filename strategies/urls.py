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

    url(r'^strategies/portfolio/(?P<path>[\w./ _!@#$%^&*(){}]*)$',
        views.StrategyPortfolioDownloadList.as_view(),
        name='strategy-portfolio-download'),

    url(r'^filter_options/$',
        views.FilterOptionList.as_view(),
        name='filteroption-list'),
    url(r'^filter_options/(?P<pk>[0-9]+)/$',
        views.FilterOptionDetail.as_view(),
        name='filteroption-detail'),
    url(r'^filter_options/all/$',
        views.FilterOptionAllList.as_view(),
        name='filteroption-list-all'),

    url(r'^stock_pickings/$',
        views.StockPickingList.as_view(),
        name='stockpicking-list'),
    url(r'^stock_pickings/(?P<pk>[0-9]+)/$',
        views.StockPickingDetail.as_view(),
        name='stockpicking-detail'),

    url('sql_query/',
        views.SqlQuery.as_view(),
        name='sql-query'),

])