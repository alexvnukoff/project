import os
import logging

from django.db.models import Q
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.db import transaction, IntegrityError
from lxml.html.clean import clean_html
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import (permission_classes, api_view,
                                       detail_route, list_route)
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from b24online.models import (News, BusinessProposal, GalleryImage, Department,
                B2BProduct, B2BProductCategory, Banner, AdditionalPage, Company,
                Questionnaire, Question, QuestionnaireCase)
from centerpokupok.models import B2CProduct, B2CProductCategory
from tpp.DynamicSiteMiddleware import get_current_site
from usersites.redisHash import get_usersite_objects
from usersites.Api.serializers import (GallerySerializer, DepartmentSerializer,
    ListNewsSerializer, DetailNewsSerializer, ListBusinessProposalSerializer,
    DetailBusinessProposalSerializer, ListB2BProductSerializer,
    DetaiB2BlProductSerializer, ListB2CProductSerializer,
    DetaiB2ClProductSerializer, B2BProductCategorySerializer,
    B2CProductCategorySerializer, ListCouponSerializer, DetaiCouponSerializer,
    ListAdditionalPageSerializer, DetailAdditionalPageSerializer,
    ListQuestionSerializer, QuestionnaireSerializer, AtFirstAnswersSerializer,
    AtSecondAnswersSerializer, ListRecommendationSerializer)

logger = logging.getLogger(__name__)


class PaginationClass(LimitOffsetPagination):
    max_limit = 50
    default_limit = 50

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'items': data
        })


class CategoryFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.GET.get('categories', None):
            category_model = self._get_category_model(queryset.model)
            category_ids = request.GET.get('categories', None).split(',')
            filter_category_ids = []

            for category in category_model.objects.filter(pk__in=category_ids):
                filter_category_ids += self._get_category_tree(category)

            return queryset.filter(categories__in=filter_category_ids).distinct()

        return queryset

    def _get_category_tree(self, category):
        if category.is_leaf_node():
            return [category.pk]
        else:
            return category.get_descendants(include_self=True).values_list('pk', flat=True)

    def _get_category_model(self, model):
        return model._meta.get_field('categories').related_model


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.get_active_objects()
    pagination_class = PaginationClass

    def filter_queryset(self, queryset):
        organization = get_usersite_objects(typeof=True)['organization']
        return queryset.filter(organization=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListNewsSerializer
            else:
                return DetailNewsSerializer

        return None


class AdditionalPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdditionalPage.objects.all()

    def get_queryset(self):
        organization = get_usersite_objects(typeof=True)['organization']
        return organization.additional_pages

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListAdditionalPageSerializer
            else:
                return DetailAdditionalPageSerializer

        return None


class BusinessProposalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessProposal.get_active_objects()
    pagination_class = PaginationClass

    def filter_queryset(self, queryset):
        organization = get_usersite_objects(typeof=True)['organization']
        return queryset.filter(organization=organization)

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListBusinessProposalSerializer
            else:
                return DetailBusinessProposalSerializer

        return None


class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = PaginationClass
    serializer_class = GallerySerializer
    # Preventing routing exception
    queryset = GalleryImage.objects.all()

    def get_queryset(self):
        return get_current_site().user_site.organization.gallery_images


class CompanyStructureViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DepartmentSerializer
    # Preventing routing exception
    queryset = Department.objects.all()

    def get_queryset(self):
        return get_current_site().user_site.organization.departments.all() \
            .prefetch_related('vacancies', 'vacancies__user', 'vacancies__user__profile')


class B2BProductViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = PaginationClass
    queryset = B2BProduct.get_active_objects()
    filter_backends = (CategoryFilterBackend,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        organization = get_current_site().user_site.organization

        if isinstance(organization, Company):
            return queryset.filter(company=organization)
        else:
            return queryset.none()

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListB2BProductSerializer
            else:
                return DetaiB2BlProductSerializer

        return None


class B2CProductViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = PaginationClass
    queryset = B2CProduct.get_active_objects()
    filter_backends = (CategoryFilterBackend,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        organization = get_current_site().user_site.organization

        if isinstance(organization, Company):
            return queryset.filter(company=organization)
        else:
            return queryset.none()

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
        organization = get_current_site().user_site.organization
        return queryset.filter(products__company_id=organization.pk) \
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
        organization = get_usersite_objects(typeof=True)['organization']
        return queryset.filter(
                products__company_id=organization.pk
            ).order_by('level').distinct()


@api_view(['GET'])
@permission_classes((AllowAny,))
def interface(request):
    organization = get_usersite_objects(typeof=True)['organization']
    menu = [{
        'name': _('Home'),
        'href': 'home/'
    }]

    if organization.news.exists():
        menu.append({
            'name': _('News'),
            'href': 'news/'
        })

    if isinstance(organization, Company) and (organization.b2b_products.exists() or organization.b2c_products.exists()):
        sub_categories = []

        menu.append({
            'name': _('Products'),
            'href': 'products/',
            "subCategories": sub_categories
        })

        if organization.b2c_products.exists():
            sub_categories.append({
                "name": _("B2C"),
                "href": "b2c/"
            })

        if organization.b2b_products.exists():
            sub_categories.append({
                "name": _("B2B"),
                "href": "b2b/"
            })

    if organization.galleries.exists():
        menu.append({
            'name': _('Gallery'),
            'href': 'gallery/'
        })

    menu += [{
        "name": _("Structure"),
        "href": "structure/"
    }, {
        "name": _("Contacts"),
        "href": "contact/"
    }]

    return Response(menu)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = PaginationClass
    queryset = B2CProduct.get_active_objects()
    filter_backends = (CategoryFilterBackend,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        organization = get_usersite_objects(typeof=True)['organization']

        if isinstance(organization, Company):
            return queryset.filter(company=organization, coupon_dates__contains=now().date(),
                                   coupon_discount_percent__gt=0).order_by("-created_at")
        else:
            return queryset.none()

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'list':
                return ListCouponSerializer
            else:
                return DetaiCouponSerializer

        return None


@api_view(['GET'])
@permission_classes((AllowAny,))
def settings_api(request):
    usersite, template, organization = get_usersite_objects()
    result = {
        'menu': [],
        'slides': [],
        'contacts': {
            'tel': clean_html(organization.phone) if organization.phone else None,
            'email': clean_html(organization.email) if organization.email else None,
            'address': clean_html(organization.address) if organization.address else None,
            'orgName': clean_html(organization.name)
        },
        'map': None,
        "orgLogo": organization.logo.original if organization.logo else None,
        "logo": usersite.logo.original if usersite.logo else None,
        "offerIcons": [],
        "footerBanner": None,
    }

    # Deprecated
    for page in organization.additional_pages.all():
        result['menu'].append({
            'name': clean_html(page.title),
            'href': "/current",
        })

    import glob
    if usersite.slider_images:
        images = [obj.image.original for obj in usersite.slider_images.only('image')]
    else:
        static_url = "%susersites/templates" % settings.STATIC_URL
        d = template.folder_name
        images = ["%s/%s/%s" % (
                static_url,
                os.path.basename(d),
                os.path.basename(image)
            ) for image in glob.glob(d + "/*.jpg")]

    for image in images:
        result['slides'].append({
            'url': image,
        })

    if organization.location:
        lat, long = organization.location.split(',')

        result['map'] = {
            "lat": lat,
            "longt": long
        }

    # TOOD cache it
    banner_blocks = ['SITES RIGHT 1', 'SITES RIGHT 2', 'SITES RIGHT 3', 'SITES RIGHT 4', 'SITES RIGHT 5',
                     'SITES FOOTER']

    for block in banner_blocks:
        banner = Banner.objects.filter(
            site_id=usersite.pk,
            block__code=block,
            block__block_type='user_site',
            image__isnull=False
        ).order_by('?').first()

        if not banner:
            continue

        if block == 'SITES FOOTER':
            result['footerBanner'] = {
                'url': banner.image.url,
                'title': banner.title,
                'link': banner.link
            }
        else:
            result['offerIcons'].append({
                'url': banner.image.url,
                'title': banner.title,
                'link': banner.link
            })

    return Response(result)


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Rest API for Questionnaires.
    """
    queryset = Questionnaire.get_active_objects()
    serializer_class = QuestionnaireSerializer

    def filter_queryset(self, queryset):
        """
        Filter the Quest-e only for current Company.
        """
        from b24online.utils import get_company_questionnaire_qs

        organization = get_current_site().user_site.organization
        return get_company_questionnaire_qs(organization)

    @detail_route(methods=['GET', ])
    def recommendations(self, request, pk=None):
        """
        Return the Questionnaire's recommendations
        """
        instance = self.get_object()
        queryset = instance.recommendations.all()
        serializer = ListRecommendationSerializer(queryset, many=True)
        return Response(serializer.data)

    def _get_questions(self, instance):
        return instance.questions\
            .filter((Q(who_created=Question.BY_AUTHOR) | \
                     Q(is_approved=True)),
                    is_active=True, is_deleted=False)

    @detail_route(methods=['GET', 'POST'])
    def inviter(self, request, pk=None):
        """
        Return the Questionnaire's questions
        """
        instance = self.get_object()
        questions = self._get_questions(instance)
        if request.method == 'POST':
            data = request.data.copy()
            data['questionnaire_id'] = instance.id
            serializer = AtFirstAnswersSerializer(data=data)
            if serializer.is_valid():
                new_questionnaire_case = serializer.save()
                return Response(
                    {'result': 'success',
                     'case_id': new_questionnaire_case.id,
                     'case_uuid': new_questionnaire_case.case_uuid})
            else:
                return Response({'result': 'error',
                                 'errors': serializer.errors})

        serializer = ListQuestionSerializer(questions, many=True)
        return Response(serializer.data)


class QuestionnaireInviterView(APIView):
    """
    Process the participants questions answers.
    """
    def _get_questions(self, instance):
        extra_ids = [q.id for q in instance.extra_questions.all()]
        return instance.questionnaire.questions\
            .filter((Q(who_created=Question.BY_AUTHOR) | \
                Q(id__in=extra_ids)),
                is_active=True, is_deleted=False)

    def get(self, request, uuid, format=None):
        try:
            instance = QuestionnaireCase.objects.get(case_uuid=uuid)
        except QuestionnaireCase.DoesNotExist:
            return Response({'result': 'error',
                'errors': [
                    _('There is no such QuestionnaireCase with UUID=%d') % \
                        uuid]})
        else:
            questions = self._get_questions(instance)
            serializer = ListQuestionSerializer(questions, many=True)
            return Response(serializer.data)

    def post(self, request, uuid, format=None):
        try:
            instance = QuestionnaireCase.objects.get(case_uuid=uuid)
        except QuestionnaireCase.DoesNotExist:
            return Response({'result': 'error',
                'errors': [
                    _('There is no such QuestionnaireCase with UUID=%d') % \
                        uuid]})
        else:
            data = request.data.copy()
            data['questionnaire_case_id'] = instance.id
            serializer = AtSecondAnswersSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                if instance:
                    serializer.process_answers(instance)
                    return Response(
                        {'result': 'success',}
                    )
                else:
                    return Response({'result': 'error',
                                     'errors': [
                                         'There is an error at saving',
                                     ]})
            else:
                return Response({'result': 'error', 'errors': serializer.errors})


class QuestionnaireCaseRecommendationsView(APIView):
    """
    Process the participants questions answers.
    """
    def get(self, request, pk, format=None, **kwargs):
        logger.debug(pk)
        logger.debug(kwargs)
        try:
            instance = QuestionnaireCase.objects.get(pk=pk)
        except QuestionnaireCase.DoesNotExist:
            return Response({'result': 'error',
                'errors': [
                    _('There is no such QuestionnaireCase with ID=%s') % \
                        pk]})
        else:
            serializer = ListRecommendationSerializer(
                instance.recommendations.all(),
                many=True
            )
            return Response(serializer.data)

