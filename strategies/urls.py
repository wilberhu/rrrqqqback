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
    url(r'^strategies/(?P<pk>[0-9]+)/highlight/$',
        views.StrategyHighlight.as_view(),
        name='strategy-highlight'),
    url(r'^strategies/(?P<pk>[0-9]+)/result/$',
        views.ResultUrl.as_view(),
        name='strategy-result-url'),
    url(r'^strategies/(?P<pk>[0-9]+)/image/$',
        views.ImageUrl.as_view(),
        name='strategy-image-url'),
    url(r'^strategy_data/$',
        views.StrategyCompare.as_view(),
        name='strategy-data')




])