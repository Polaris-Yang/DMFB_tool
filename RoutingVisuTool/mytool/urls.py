from django.conf.urls import url, re_path
from django.urls import path

from . import views

urlpatterns = [
    url(r'index.html', views.index),
    url(r'verification.html', views.verify),
    url(r'get1/$', views.get1),
    url(r'get2/$', views.get2),
    url(r'^tmp/$', views.learn_temp, name='tmp'),

]