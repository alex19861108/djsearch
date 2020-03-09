"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  urls.py
@Description    :  
@CreateTime     :  2020/3/7 11:43
"""
from django.urls import path
from searcher.views import IndicesView, SearchView, SugView

urlpatterns = [
    path('indices', IndicesView.as_view()),
    path('search', SearchView.as_view()),
    path('sug', SugView.as_view()),
]
