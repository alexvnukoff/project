from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from usersites.Api.views import NewsViewSet, BusinessProposalViewSet, GalleryViewSet, CompanyStructureViewSet, \
    B2CProductViewSet, B2BProductViewSet, B2BProductCategoryViewSet, B2CProductCategoryViewSet, interface, \
    CouponViewSet, settings_api, AdditionalPageViewSet, QuestionnaireViewSet, \
    QuestionnaireInviterView, QuestionnaireCaseRecommendationsView


urlpatterns = [
    url(r'^$', interface),
    url(r'^settings/$', settings_api),

    # Authentication (login/logout)
    url(r'^api-auth/', include('rest_framework.urls', 
        namespace='rest_framework')),
    url(r'^questionnaires/(?P<uuid>[0-9a-f\-]+?)/invited/$', 
        QuestionnaireInviterView.as_view(),
        name='questionnaire-invited'),
    url(r'^questionnaires/case/(?P<pk>[0-9]+?)/recommendations/$', 
        QuestionnaireCaseRecommendationsView.as_view(),
        name='questionnaire-case-recommendations'),
]

router = DefaultRouter()
router.register(r'pages', AdditionalPageViewSet)
router.register(r'news', NewsViewSet)
router.register(r'offers', BusinessProposalViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'structure', CompanyStructureViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'products/b2b/categories', B2BProductCategoryViewSet)
router.register(r'products/b2c/categories', B2CProductCategoryViewSet)
router.register(r'products/b2b', B2BProductViewSet)
router.register(r'products/b2c', B2CProductViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)

urlpatterns += router.urls
