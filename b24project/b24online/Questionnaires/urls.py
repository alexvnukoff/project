# -*- encoding: utf-8 -*-

"""
URLs for Questions sub-app.
"""

from django.conf.urls import url

from b24online.Questionnaires.views import (
     QuestionnaireList,
     QuestionnaireCreate,
     QuestionnaireDetail,
     QuestionnaireUpdate,
     QuestionnaireDelete,
     QuestionList,
     QuestionCreate,
)


urlpatterns = [
     url(r'^$', QuestionnaireList.as_view(), name='main'),
     url(r'^list/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)/$',
         QuestionnaireList.as_view(), 
         name='list'),
     url(r'^list/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)'
         r'/page(?P<page>[0-9]+)?/$',
         QuestionnaireList.as_view(), 
         name="list_paginator"),
     url(r'^add/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)/$',
         QuestionnaireCreate.as_view(), 
         name='add'),
     url(r'^detail/(?P<item_id>\d+?)/$',
         QuestionnaireDetail.as_view(), 
         name='detail'),
     url(r'^update/(?P<item_id>\d+?)/$',
         QuestionnaireUpdate.as_view(), 
         name='update'),
     url(r'^delete/(?P<item_id>\d+?)/$',
         QuestionnaireDelete.as_view(), 
         name='delete'),
     url(r'^detail/(?P<item_id>\d+?)/questions/$',
         QuestionList.as_view(), 
         name='questions'),
     url(r'^detail/(?P<item_id>\d+?)/questions/add/$',
         QuestionCreate.as_view(), 
         name='add_question'),
]