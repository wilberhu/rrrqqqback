from django.conf.urls import url

from users import views

urlpatterns = [

    url(r'^users/$',
        views.UserList.as_view(),
        name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$',
        views.UserDetail.as_view(),
        name='user-detail'),

    url(r'^user/login', views.user_login),
    url(r'^user/info', views.user_info),
    url(r'^user/logout', views.user_logout),
    url(r'^user/user_head_portrait/(?P<pk>[^/]+)/$',
        views.ImageUrl.as_view(),
        name='user-head-portrait'),

    url(r'^token/$',
        views.TokenView.as_view(),
        name='token'),
    url(r'^password_change/$',
        views.PasswordChangeView.as_view(),
        name='password-change'),
]


# from django.contrib.auth import views
# urlpatterns += [
#     url(r'^password_change/$',
#         views.PasswordChangeView.as_view(template_name='admin/password_change.html', success_url='/'),
#         name='password-change'),
# ]