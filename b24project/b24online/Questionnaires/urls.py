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
     url(r'^add/$', QuestionnaireCreate.as_view(), name='add'),
]