from django.conf.urls import url

import b24online.TppTV.views

urlpatterns = [
    url(r'^$', b24online.TppTV.views.TVNewsLIst.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', b24online.TppTV.views.TVNewsLIst.as_view(), name="paginator"),
    url(r'^add/$', b24online.TppTV.views.TvCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', b24online.TppTV.views.TvUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', b24online.TppTV.views.NewsDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.TppTV.views.TVNewsDetail.as_view(),
        name="detail"),
]
