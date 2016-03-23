# -*- encoding: utf-8 -*-

from django.conf.urls import url

from usersites.Questionnaires.views import (
    QuestionnaireDetail,
    QuestionnaireReady,
    QuestionnaireActivate,
    QuestionnaireResults,
    QuestionnaireCaseList,
)    
    

urlpatterns = [
     url(r'^cases/$',
         QuestionnaireCaseList.as_view(), 
         name='case_list'),
     url(r'^cases/page(?P<page>[0-9]+)?/$',
         QuestionnaireCaseList.as_view(), 
         name='case_list_paginator'),
     url(r'^detail/(?P<item_id>\d+?)/$',
         QuestionnaireDetail.as_view(), 
         name='detail'),
     url(r'^answers/(?P<uuid>[0-9a-f\-]+?)/$',
         QuestionnaireDetail.as_view(), 
         name='invited_answers'),
     url(r'^ready/(?P<uuid>.+?)/$',
         QuestionnaireReady.as_view(), 
         name='ready'),
     url(r'^activate/(?P<uuid>.+?)/$',
         QuestionnaireActivate.as_view(), 
         name='activate'),
     url(r'^results/(?P<uuid>.+?)/(?P<participant>inviter|invited)/$',
         QuestionnaireResults.as_view(), 
         name='results'),
]
