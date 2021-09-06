from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from tush import views
from django.conf.urls import include

urlpatterns = format_suffix_patterns([

    url(r'^companies/$',
        views.CompanyList.as_view(),
        name='company-list'),
    url(r'^companies/query/$',
        views.CompanyQuery.as_view(),
        name='company-query-list'),
    url(r'^companies/(?P<pk>[\w.]+)/$',
        views.CompanyDetail.as_view(),
        name='company-detail'),
    url(r'^companies/hist_data/(?P<ts_code>[\w.]+)',
        views.CompanyHistData.as_view(),
        name='company-hist-data'),
    url(r'^indexes/$',
        views.IndexList.as_view(),
        name='index-list'),
    url(r'^indexes/query/$',
        views.IndexQuery.as_view(),
        name='index-query-list'),
    url(r'^indexes/(?P<pk>[\w.]+)/$',
        views.IndexDetail.as_view(),
        name='index-detail'),
    url(r'^indexes/hist_data/(?P<ts_code>[\w.]+)',
        views.IndexHistData.as_view(),
        name='index-hist-data'),

    url(r'^companies_daily/$',
        views.CompanyDailyList.as_view(),
        name='companydaily-list'),
    url(r'^indexes_daily/$',
        views.IndexDailyList.as_view(),
        name='indexdaily-list'),

    url(r'^companies_daily_basic/$',
        views.CompanyDailyBasicList.as_view(),
        name='companydailybasic-list'),
    url(r'^indexes_daily_basic/$',
        views.IndexDailyBasicList.as_view(),
        name='indexdailybasic-list'),

    url(r'^funds_basic/$',
        views.FundBasicList.as_view(),
        name='fundbasic-list'),
    url(r'^funds_basic/query/$',
        views.FundBasicQuery.as_view(),
        name='fundbasic-query-list'),
    url(r'^funds_basic/(?P<pk>[0-9]+)/$',
        views.FundBasicDetail.as_view(),
        name='fundbasic-detail'),
    url(r'^funds_basic/hist_data/(?P<ts_code>[\w.]+)',
        views.FundBasicHistData.as_view(),
        name='fundbasic-hist-data'),

    url(r'^funds_basic/portfolio/(?P<ts_code>[\w.]+)/$',
        views.FundPortfolioList.as_view(),
        name='fundbasic-portfolio'),

    url(r'^funds_basic/portfolio/(?P<ts_code>[\w.]+)/download/$',
        views.FundPortfolioDownloadList.as_view(),
        name='fundbasic-portfolio-download'),

    url(r'^funds_daily/$',
        views.FundDailyList.as_view(),
        name='funddaily-list'),
    url(r'^funds_nav/$',
        views.FundNavList.as_view(),
        name='fundnav-list'),

    url(r'^funds/(?P<column>[\w.]+)/$',
        views.FundNavData.as_view(),
        name='fund-nav-data'),

    url(r'^data/(?P<column>[\w.]+)/$',
        views.CloseData.as_view(),
        name='close-data'),
])