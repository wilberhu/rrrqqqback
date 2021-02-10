from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from compositions import views

urlpatterns = format_suffix_patterns([

    url(r'^compositions/$',
        views.CompositionList.as_view(),
        name='composition-list'),
    url(r'^compositions/(?P<pk>[0-9]+)/$',
        views.CompositionDetail.as_view(),
        name='composition-detail'),
    url(r'^compositions/calculate/$',
        views.CompositionCalculate.as_view(),
        name='composition-calculate'),
    url(r'^compositions/dataframe/$',
        views.CompositionDataframe.as_view(),
        name='composition-dataframe'),
    url(r'^trade_calender/$',
        views.TradeCalender.as_view(),
        name='trade-calender'),
])