from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from dailies import views
from django.conf.urls import include

urlpatterns = format_suffix_patterns([
    url(r'^companies_daily/$',
        views.CompanyDailyList.as_view(),
        name='companydaily-list'),
    url(r'^companies_daily/(?P<pk>[0-9]+)/$',
        views.CompanyDailyDetail.as_view(),
        name='companydaily-detail'),
    url(r'^indexes_daily/$',
        views.IndexDailyList.as_view(),
        name='indexdaily-list'),
    url(r'^indexes_daily/(?P<pk>[0-9]+)/$',
        views.IndexDailyDetail.as_view(),
        name='indexdaily-detail'),

    url('sql_query/',
        views.SqlQuery.as_view(),
        name='sql-query'),

])