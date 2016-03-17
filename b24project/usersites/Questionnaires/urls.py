# -*- encoding: utf-8 -*-

from django.conf.urls import url

from usersites.Questionnaires.views import QuestionnaireDetail

urlpatterns = [
     url(r'^detail/(?P<item_id>\d+?)/$',
         QuestionnaireDetail.as_view(), 
         name='detail'),
]
