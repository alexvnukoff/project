from django.conf.urls import url

from usersites.B2BProducts.views import B2BProductList, B2BProductListDetail

urlpatterns = [
    url(r'^$', B2BProductList.as_view(), name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', B2BProductList.as_view(), name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)?/$', B2BProductList.as_view(), name="category"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)?/page(?P<page>[0-9]+)?/$', B2BProductList.as_view(),
        name="category_paged"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', B2BProductListDetail.as_view(), name='detail'),
]
