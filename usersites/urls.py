from django.conf.urls import patterns, include, url

import usersites.views
import usersites.News.urls
import usersites.Proposals.urls
import usersites.Products.urls
import usersites.Contact.urls
import usersites.CompanyStructure.urls



from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
     url(r'^$', usersites.views.get_wall, name='main'),
     url(r'^(?P<language>[a-zA-Z]{2})/$', usersites.views.get_wall, name='main_lang'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^(?P<language>[a-zA-Z]{2})/news/', include(usersites.News.urls, namespace='news_lang')),
    url(r'^news/', include(usersites.News.urls, namespace='news')),

    url(r'^proposal/', include(usersites.Proposals.urls, namespace='proposal')),
    url(r'^(?P<language>[a-zA-Z]{2})/proposal/', include(usersites.Proposals.urls, namespace='proposal_lang')),

    url(r'^products/', include(usersites.Products.urls, namespace='products')),
    url(r'^(?P<language>[a-zA-Z]{2})/products/', include(usersites.Products.urls, namespace='products_lang')),

    url(r'^contact/', include(usersites.Contact.urls, namespace='contact')),
    url(r'^(?P<language>[a-zA-Z]{2})/contact/', include(usersites.Contact.urls, namespace='contact_lang')),

    url(r'^structure/', include(usersites.CompanyStructure.urls, namespace='structure')),
    url(r'^(?P<language>[a-zA-Z]{2})/structure/', include(usersites.CompanyStructure.urls, namespace='structure_lang')),

    url(r'^page-(?P<page_id>[0-9]+)/$', usersites.views.get_wall, name='additionalPage'),
    url(r'^(?P<language>[a-zA-Z]{2})/page-(?P<page_id>[0-9]+)/', usersites.views.get_wall, name='additionalPage_lang'),
)
