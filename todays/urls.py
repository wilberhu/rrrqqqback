from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from todays import views
from django.conf.urls import include

urlpatterns = format_suffix_patterns([
    url(r'^companies_today/$',
        views.CompanyTodayList.as_view(),
        name='companytoday-list'),
    url(r'^companies_today/(?P<pk>[0-9]+)/$',
        views.CompanyTodayDetail.as_view(),
        name='companytoday-detail'),
    url(r'^indexes_today/$',
        views.IndexTodayList.as_view(),
        name='indextoday-list'),
    url(r'^indexes_today/(?P<pk>[0-9]+)/$',
        views.IndexTodayDetail.as_view(),
        name='indextoday-detail'),
])