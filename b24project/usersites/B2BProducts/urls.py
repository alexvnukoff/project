from django.conf.urls import url
from django.utils.translation import ugettext as _
from usersites.views import render_page
from usersites.B2BProducts.views import B2BProductListDetail, B2BCategoriesView

urlpatterns = [
    url(r'^$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<category>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="category"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<category>[0-9]+)?/page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="category_paged"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<pk>[0-9]+)\.html$', B2BProductListDetail.as_view(), name='detail'),
    url(r'^categories/$', B2BCategoriesView.as_view(), name='categories'),

    url(r'^$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name='main'),
    url(r'^page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="paginator"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<category>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="category"),
    url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<category>[0-9]+)?/page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/contentPage.html', 'title': _("B2B Products")}, name="category_paged"),
    url(r'^search/$', render_page,
        kwargs={'template': 'B2BProducts/searchPage.html', 'title': _("B2B Products")}, name="search"),
    url(r'^search/page(?P<page>[0-9]+)?/$', render_page,
        kwargs={'template': 'B2BProducts/searchPage.html', 'title': _("B2B Products")}, name="search_paginator"),

]
