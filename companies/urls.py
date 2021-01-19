from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from companies import views
from django.conf.urls import include

urlpatterns = format_suffix_patterns([

    url(r'^companies/$',
        views.CompanyList.as_view(),
        name='company-list'),

    url(r'^companies/all/$',
        views.CompanyAllList.as_view(),
        name='company-all-list'),

    url(r'^companies/(?P<pk>[\w.]+)/$',
        views.CompanyDetail.as_view(),
        name='company-detail'),

    url(r'^companies/hist_data/(?P<ts_code>\w+)',
        views.CompanyHistData.as_view(),
        name='company-hist-data'),

    url(r'^indexes/$',
        views.IndexList.as_view(),
        name='index-list'),

    url(r'^indexes/all/$',
        views.IndexAllList.as_view(),
        name='index-all-list'),

    url(r'^indexes/(?P<pk>[\w.]+)/$',
        views.IndexDetail.as_view(),
        name='index-detail'),

    url(r'^indexes/hist_data/(?P<ts_code>[\w.]+)',
        views.IndexHistData.as_view(),
        name='index-hist-data'),

    url(r'^data/(?P<column>[\w.]+)/$',
        views.CloseData.as_view(),
        name='close-data'),

    url(r'^item_hist_data/(?P<ts_code>[\w.]+)',
        views.ItemHistData.as_view(),
        name='item-hist-data'),
])