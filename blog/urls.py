from django.urls import re_path
from . import views

urlpatterns = [
    re_path('^$', views.post_list, name='post_list'),
    re_path('^@(?P<author>[\._\w-]+)/(?P<permlink>[\._\w-]+)/$', views.post_detail, name='post_detail')
]