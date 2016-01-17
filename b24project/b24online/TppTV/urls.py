from django.conf.urls import url

from b24online.TppTV.views import TVNewsLIst, TvUpdate, NewsDelete, TvCreate, TVNewsDetail

urlpatterns = [
    url(r'^$', TVNewsLIst.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', TVNewsLIst.as_view(), name="paginator"),
    url(r'^add/$', TvCreate.as_view(), name="add"),
    url(r'^update/(?P<pk>[0-9]+)/$', TvUpdate.as_view(), name="update"),
    url(r'^delete/(?P<pk>[0-9]+)/$', NewsDelete.as_view(), name="delete"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', TVNewsDetail.as_view(), name="detail"),
]
