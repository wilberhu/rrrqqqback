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

    url(r'^filter_options/$',
        views.FilterOptionList.as_view(),
        name='filteroption-list'),
    url(r'^filter_options/(?P<pk>[0-9]+)/$',
        views.FilterOptionDetail.as_view(),
        name='filteroption-detail'),

    url(r'^strategy_filter/$',
        views.StrategyFilter.as_view(),
        name='strategy-filter'),

    url('sql_query/',
        views.SqlQuery.as_view(),
        name='sql-query'),

])