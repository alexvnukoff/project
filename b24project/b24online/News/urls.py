from django.conf.urls import patterns, url
from django.contrib import admin

import b24online.News.views

admin.autodiscover()


urlpatterns = patterns('',
     url(r'^$', b24online.News.views.NewsList.as_view(), name='main'),
     url(r'^page(?P<page>[0-9]+)?/$', b24online.News.views.NewsList.as_view(), name="paginator"),
     url(r'^my/$', b24online.News.views.NewsList.as_view(my=True), name='my_main'),
     url(r'^my/page(?P<page>[0-9]+)?/$', b24online.News.views.NewsList.as_view(my=True), name="my_main_paginator"),
     url(r'^add/$', b24online.News.views.NewsCreate.as_view(), name="add"),
     url(r'^category/(?P<category>[0-9]+)/$', b24online.News.views.NewsList.as_view(),  name='news_categories'),
     url(r'^category/(?P<category>[0-9]+)/page(?P<page>[0-9]+)?/$', b24online.News.views.NewsList.as_view(), name="news_categories_paginator"),
     url(r'^update/(?P<pk>[0-9]+)/$', b24online.News.views.NewsUpdate.as_view(),{'action': 'update'}, name="update"),
     url(r'^delete/(?P<pk>[0-9]+)/$', b24online.News.views.DeleteNews.as_view(), name="delete"),
     url(r'^(?P<slug>[a-zA-z0-9-]+)-(?P<item_id>[0-9]+)\.html$', b24online.News.views.NewsDetail.as_view(), name="detail"),

     url(r'^tabs/gallery/(?P<item>[0-9]+)/$', b24online.News.views.NewsGalleryImageList.as_view(), name="tabs_gallery"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.News.views.NewsGalleryImageList.as_view(), name="tabs_gallery_paged"),
     url(r'^tabs/gallery_structure/(?P<item>[0-9]+)/page(?P<page>[0-9]+)/$', b24online.News.views.NewsGalleryImageList.as_view(is_structure=True), name="gallery_structure"),
     url(r'^tabs/gallery/(?P<item>[0-9]+)/remove/(?P<pk>[0-9]+)/$', b24online.News.views.DeleteNewsGalleryImage.as_view(), name="gallery_remove_item"),

)