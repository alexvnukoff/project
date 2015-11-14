from django.contrib.sites.shortcuts import get_current_site
from rest_framework import viewsets
from rest_framework.response import Response

from b24online.models import News, BusinessProposal, GalleryImage, Department, B2BProduct, B2BProductCategory
from centerpokupok.models import B2CProduct, B2CProductCategory
from usersites.Api.serializers import GallerySerializer, \
    DepartmentSerializer, ListNewsSerializer, DetailNewsSerializer, ListBusinessProposalSerializer, \
    DetailBusinessProposalSerializer, ListB2BProductSerializer, DetaiB2BlProductSerializer, ListB2CProductSerializer, \
    DetaiB2ClProductSerializer, B2BProductCategorySerializer, B2CProductCategorySerializer


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(organization=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListNewsSerializer
            else:
                return DetailNewsSerializer

        return None


class BusinessProposalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessProposal.objects.all()

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(organization=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListBusinessProposalSerializer
            else:
                return DetailBusinessProposalSerializer

        return None


class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GallerySerializer
    # Preventing routing exception
    queryset = GalleryImage.objects.all()

    def get_queryset(self):
        return get_current_site(self.request).user_site.organization.gallery_images


class CompanyStructureViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    # Preventing routing exception
    queryset = Department.objects.all()

    def get_queryset(self):
        return get_current_site(self.request).user_site.organization.departments.all() \
            .prefetch_related('vacancies', 'vacancies__user', 'vacancies__user__profile')


class B2BProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = B2BProduct.objects.all()

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(company=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListB2BProductSerializer
            else:
                return DetaiB2BlProductSerializer

        return None


class B2CProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = B2CProduct.objects.all()

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(company=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListB2CProductSerializer
            else:
                return DetaiB2ClProductSerializer

        return None


class B2BProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = B2BProductCategory.objects.all()
    serializer_class = B2BProductCategorySerializer

    def _load_category_hierarchy(self, categories, loaded_categories=None):

        if not loaded_categories:
            loaded_categories = {}

        categories_to_load = []

        for category in categories:
            loaded_categories[category.pk] = category

            if category.parent_id and category.parent_id not in loaded_categories:
                categories_to_load.append(category.parent_id)

        if categories_to_load:
            queryset = B2BProductCategory.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self._load_category_hierarchy(queryset).values(), many=True)

        return Response(serializer.data)

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(products__company_id=organization.pk)\
            .order_by('level').distinct()


class B2CProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = B2CProductCategory.objects.all()
    serializer_class = B2CProductCategorySerializer

    def _load_category_hierarchy(self, categories, loaded_categories=None):

        if not loaded_categories:
            loaded_categories = {}

        categories_to_load = []

        for category in categories:
            loaded_categories[category.pk] = category

            if category.parent_id and category.parent_id not in loaded_categories:
                categories_to_load.append(category.parent_id)

        if categories_to_load:
            queryset = B2CProductCategory.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self._load_category_hierarchy(queryset).values(), many=True)

        return Response(serializer.data)

    def filter_queryset(self, queryset):
        organization = get_current_site(self.request).user_site.organization
        return queryset.filter(products__company_id=organization.pk)\
            .order_by('level').distinct()