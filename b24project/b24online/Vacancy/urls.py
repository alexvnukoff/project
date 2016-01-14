from django.conf.urls import url

import b24online.Vacancy.views

urlpatterns = [url(r'^$', b24online.Vacancy.views.RequirementList.as_view(), name='main'),
               url(r'^page(?P<page>[0-9]+)?/$', b24online.Vacancy.views.RequirementList.as_view(), name="paginator"),
               url(r'^my/$', b24online.Vacancy.views.RequirementList.as_view(my=True), name='my_main'),
               url(r'^my/page(?P<page>[0-9]+)?/$', b24online.Vacancy.views.RequirementList.as_view(my=True),
                   {'my': True}, name="my_main_paginator"),
               url(r'^add/$', b24online.Vacancy.views.RequirementCreate.as_view(), name="add"),
               url(r'^update/(?P<pk>[0-9]+)/$', b24online.Vacancy.views.RequirementUpdate.as_view(), name="update"),
               url(r'^delete/(?P<pk>[0-9]+)/$', b24online.Vacancy.views.RequirementDelete.as_view(), name="delete"),
               url(r'^send/$', b24online.Vacancy.views.send_resume, name="send"),
               url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$',
                   b24online.Vacancy.views.RequirementDetail.as_view(), name="detail"),
               ]
