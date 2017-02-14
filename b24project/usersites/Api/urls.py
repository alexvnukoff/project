# -*- encoding: utf-8 -*-
import logging
from django.conf.urls import include, url
from rest_framework import routers, serializers, viewsets
from usersites.Api.views import (NewsViewSet, BusinessProposalViewSet,
    GalleryViewSet, CompanyStructureViewSet, B2CProductViewSet,
    B2BProductViewSet, B2BProductCategoryViewSet, B2CProductCategoryViewSet,
    interface, CouponViewSet, settings_api, AdditionalPageViewSet,
    QuestionnaireViewSet, QuestionnaireInviterView,
    QuestionnaireCaseRecommendationsView)

logger = logging.getLogger(__name__)

router = routers.DefaultRouter()
router.register(r'pages', AdditionalPageViewSet)
router.register(r'news', NewsViewSet)
router.register(r'offers', BusinessProposalViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'structure', CompanyStructureViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'b2b/categories', B2BProductCategoryViewSet)
router.register(r'b2c/categories', B2CProductCategoryViewSet)
router.register(r'b2b', B2BProductViewSet)
router.register(r'b2c', B2CProductViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)

urlpatterns = [

    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),

    # url(r'^$', interface),
    # url(r'^settings/$', settings_api),
    # Questionnaires
    url(r'^questionnaires/(?P<uuid>[0-9a-f\-]+?)/invited/$',
        QuestionnaireInviterView.as_view(),
        name='questionnaire-invited'),
    url(r'^questionnaires/case/(?P<pk>[0-9]+?)/recommendations/$',
        QuestionnaireCaseRecommendationsView.as_view(),
        name='questionnaire-case-recommendations'),
]

