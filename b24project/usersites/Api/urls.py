from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter
from usersites.Api.views import NewsViewSet, BusinessProposalViewSet, GalleryViewSet, CompanyStructureViewSet, \
    B2CProductViewSet, B2BProductViewSet, B2BProductCategoryViewSet, B2CProductCategoryViewSet, interface

urlpatterns = patterns('',
                       url(r'^', interface)
                       )

router = DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'offers', BusinessProposalViewSet)
router.register(r'gallery', GalleryViewSet)
router.register(r'structure', CompanyStructureViewSet)
router.register(r'b2b/products', B2BProductViewSet)
router.register(r'b2c/products', B2CProductViewSet)
router.register(r'b2b/categories', B2BProductCategoryViewSet)
router.register(r'b2c/categories', B2CProductCategoryViewSet)

urlpatterns += router.urls
