# -*- encoding: utf-8 -*-

"""
URLs for Questions sub-app.
"""

from django.conf.urls import url

from b24online.Questionnaires.views import (
     QuestionnaireList,
     QuestionnaireCreate,
     QuestionnaireUpdate,
)


urlpatterns = [
     url(r'^$', QuestionnaireList.as_view(), name='main'),
     url(r'^list/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)/$',
         QuestionnaireList.as_view(), 
         name='list_for_item'),
     url(r'^add/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)/$',
         QuestionnaireCreate.as_view(), 
         name='add_for_item'),
     url(r'^detail/(?P<pk>\d+?)/$',
         QuestionnaireUpdate.as_view(), 
         name='update'),
]