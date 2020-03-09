"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  urls.py
@Description    :  
@CreateTime     :  2020/3/7 12:27
"""
from django.urls import path
from crawler import views

urlpatterns = [
    path('portal', views.api_portal),
    path('mp_e/header/getApp', views.mock_get_app),
]
