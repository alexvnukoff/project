# -*- encoding: utf-8 -*-

"""
URLs for Questions sub-app.
"""

from django.conf.urls import url

from b24online.Questionnaires.views import (
     QuestionnaireList,
     QuestionnaireCreate
)


urlpatterns = [
     url(r'^$', QuestionnaireList.as_view(), name='main'),
     url(r'^add/(?P<content_type_id>\d+?)/(?P<item_id>\d+?)/$',
         QuestionnaireCreate.as_view(), 
         name='add_for_object'),
]