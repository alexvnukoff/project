from django.conf.urls import patterns, include, url

import usersites.views
import usersites.OrganizationPages.urls
import usersites.News.urls
import usersites.Proposals.urls
import usersites.Products.urls
import usersites.Contact.urls
import usersites.CompanyStructure.urls

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', usersites.views.get_wall, name='main'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^(?P<language>[a-zA-Z]{2})/news/', include(usersites.News.urls, namespace='news_lang')),
                       url(r'^news/', include(usersites.News.urls, namespace='news')),
                       url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
                       url(r'^products/', include(usersites.Products.urls, namespace='products')),
                       url(r'^contact/', include(usersites.Contact.urls, namespace='contact')),
                       url(r'^structure/', include(usersites.CompanyStructure.urls, namespace='structure')),
                       url(r'^pages/', include(usersites.OrganizationPages.urls, namespace='additionalPage')),
                       )

import debug_toolbar

urlpatterns += patterns('',
                        url(r'^__debug__/', include(debug_toolbar.urls)),
                        )
