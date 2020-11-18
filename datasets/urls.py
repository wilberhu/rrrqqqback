from django.conf.urls import url
from datasets import views

# API endpoints
urlpatterns = [
    url(r'^datasets/$',
        views.datasetList.as_view(),
        name='dataset-list'),
    url(r'^datasets/(?P<pk>[0-9]+)/$',
        views.datasetDetail.as_view(),
        name='dataset-detail'),
    url(r'^datasets_delete/$',
        views.datasetDelete.as_view(),
        name='dataset-delete'),
    url(r'^datasets/(?P<pk>[0-9]+)/highlight/$',
         views.datasetHighlight.as_view(),
         name='dataset-highlight'),
]