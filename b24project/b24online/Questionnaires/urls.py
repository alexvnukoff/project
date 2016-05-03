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
     QuestionCreate,
     QuestionUpdate,
     QuestionDelete,
     RecommendationCreate,
     RecommendationUpdate,
     RecommendationDelete,
     questionnaire_case_answers,
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
     url(r'^update/(?P<pk>\d+?)/$',
         QuestionnaireUpdate.as_view(), 
         name='update'),
     url(r'^delete/(?P<pk>\d+?)/$',
         QuestionnaireDelete.as_view(), 
         name='delete'),
     url(r'^detail/(?P<item_id>\d+?)/questions/add/$',
         QuestionCreate.as_view(), 
         name='add_question'),
     url(r'^questions/update/(?P<pk>\d+?)/$',
         QuestionUpdate.as_view(), 
         name='update_question'),
     url(r'^questions/delete/(?P<pk>\d+?)/$',
         QuestionDelete.as_view(), 
         name='delete_question'),
     url(r'^detail/(?P<item_id>\d+?)/recommendations/add/$',
         RecommendationCreate.as_view(), 
         name='add_recommendation'),
     url(r'^recommendations/update/(?P<pk>\d+?)/$',
         RecommendationUpdate.as_view(), 
         name='update_recommendation'),
     url(r'^recommendations/delete/(?P<pk>\d+?)/$',
         RecommendationDelete.as_view(), 
         name='delete_recommendation'),
     url(r'^case/(?P<pk>\d+?)/answers/(?P<participant_type>(inviter|invited))/$',
         questionnaire_case_answers, 
         name='questionnaire_case_answers'),
 
]