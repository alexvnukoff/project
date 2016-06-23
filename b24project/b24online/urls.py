# -*- encoding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from loginas.views import user_login
from django.views.generic import TemplateView
import b24online.AdminTpp
import b24online.AdminTpp.urls
import b24online.AdvBanner
import b24online.AdvBanner.urls
import b24online.AdvTop
import b24online.AdvTop.urls
import b24online.Analytic
import b24online.Analytic.urls
import b24online.BusinessProposal.urls
import b24online.Companies.urls
import b24online.Exhibitions.urls
import b24online.Greetings
import b24online.Greetings.urls
import b24online.Innov.urls
import b24online.Messages
import b24online.Messages.urls
import b24online.News.urls
import b24online.Payments.urls
import b24online.Product.urls
import b24online.Profile.urls
import b24online.Project
import b24online.Project.urls
import b24online.Questionnaires.urls
import b24online.Resume.urls
import b24online.Tenders.urls
import b24online.Tpp.urls
import b24online.TppTV.urls
import b24online.UserSites.urls
import b24online.Users.urls
import b24online.Vacancy.urls
import b24online.Wall.urls
import b24online.Video.urls
import b24online.views

admin.autodiscover()

urlpatterns = [
    url(r'^$', b24online.views.home, name="main"),
    url(r"^login/user/(?P<user_id>.+)/$", user_login, name="loginas-user-login"),
    url(r'^news/', include(b24online.News.urls, namespace='news')),
    url(r'^products/', include(b24online.Product.urls, namespace='products')),
    url(r'^innovation/', include(b24online.Innov.urls, namespace='innov')),
    url(r'^companies/', include(b24online.Companies.urls, namespace='companies')),
    url(r'^tpp/', include(b24online.Tpp.urls, namespace='tpp')),
    url(r'^proposal/', include(b24online.BusinessProposal.urls, namespace='proposal')),
    url(r'^exhibitions/', include(b24online.Exhibitions.urls, namespace='exhibitions')),
    url(r'^tenders/', include(b24online.Tenders.urls, namespace='tenders')),
    url(r'^vacancy/', include(b24online.Vacancy.urls, namespace='vacancy')),
    url(r'^tv/', include(b24online.TppTV.urls, namespace='tv')),
    url(r'^profile/', include(b24online.Profile.urls, namespace='profile')),
    url(r'^wall/', include(b24online.Wall.urls, namespace='wall')),
    url(r'^greetings/', include(b24online.Greetings.urls, namespace='greetings')),
    url(r'^analytic/', include(b24online.Analytic.urls, namespace='analytic')),
    url(r'^resume/', include(b24online.Resume.urls, namespace='resume')),
    url(r'^site/', include(b24online.UserSites.urls, namespace='site')),
    url(r'^users/', include(b24online.Users.urls, namespace='users')),
    url(r'^payments/', include(b24online.Payments.urls, namespace='payments')),
    url(r'^questionnaires/',
        include(b24online.Questionnaires.urls,
        namespace='questionnaires')),
    url(r'^video/', include(b24online.Video.urls, namespace='video')),
    url(r'^admin-tpp/', include(b24online.AdminTpp.urls, namespace='AdminTpp')),

    url(r'^register/exhibition/$', b24online.views.register_to_exhibition),

    url(r'^denied/', b24online.views.perm_denied, name='denied'),

    url(r'^messages/', include(b24online.Messages.urls, namespace='messages')),
    url(r'^advbanner/', include(b24online.AdvBanner.urls, namespace='adv_banners')),
    url(r'^advtop/', include(b24online.AdvTop.urls, namespace='adv_top')),

    url(r'^project/', include(b24online.Project.urls, namespace='project')),

    url(r'^ping/', b24online.views.ping),
    url(r'^admin/tpp/', include(admin.site.urls)),

    url(r'^notification/get/$', b24online.views.get_notification_list),
    url(r'^addPage/get/$', b24online.views.get_additional_page),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^adv/tops/', b24online.views.get_live_top),
    url(r'^adv/bann/', b24online.views.get_live_banner),
    url(r'^filter/', b24online.views.json_filter),
    url(r'^company-manage/', b24online.views.my_companies),
    url(r'^set/(?P<item_id>[0-9]+)/$', b24online.views.set_current, name="setCurrent"),
    url(r'^branch-list$', b24online.views.branch_list, name="branch_list"),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^tos/$', TemplateView.as_view(template_name="b24online/tos.html"), name="tos"),
    url(r'^upload/$', b24online.views.editor_upload, name="upload_editor_image"),
    url(r'^feedback/send/email/$', b24online.views.feedback_form),
]

if settings.DEBUG:
    import debug_toolbar
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()
