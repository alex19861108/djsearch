"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  urls.py
@Description    :  
@CreateTime     :  2020/3/7 21:16
"""
from django.urls import path
from builder import views

urlpatterns = [
    path('build', views.build),
    path('reindex', views.ReIndexView.as_view()),
]
