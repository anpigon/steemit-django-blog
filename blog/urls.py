from django.urls import re_path
from . import views

urlpatterns = [
    re_path('^$', views.post_list, name='post_list'),
    re_path(r'^@(?P<author>[\w-]+)/(?P<permlink>[\w-]+)/$', views.post_detail, name='post_detail')
]