from django.utils.functional import cached_property
from rest_framework.response import Response
from rest_framework.views import APIView

from appl import func
from b24online.api.v1.helpers import BaseListApi, FilterableViewMixin, BaseAdvertisementView
from b24online.api.v1.serializers import B2BProductSerializer, ProjectsSerializer, ProposalsSerializer, \
    ExhibitionsSerializer, NewsSerializer, CompanySerializer, ChamberSerializer, B2CProductSerializer, CouponSerializer, \
    VideoSerializer, VacancySerializer, ResumeSerializer, BannerSerializer, ContextAdvertisementSerializer
from b24online.models import InnovationProject, B2BProduct, BusinessProposal, Exhibition, News, Company, Chamber, \
    VideoChannel, Country, Branch
from b24online.search_indexes import SearchEngine
from centerpokupok.models import B2CProduct, Coupon
from jobs.models import Requirement, Resume


class Wall(APIView, FilterableViewMixin):
    sorting = ('-created_at',)

    projects_queryset = InnovationProject.get_active_objects() \
        .prefetch_related('organization', 'organization__countries')

    products_queryset = B2BProduct.get_active_objects().prefetch_related('company__countries')

    proposals_queryset = BusinessProposal.get_active_objects() \
        .prefetch_related('branches', 'organization', 'organization__countries')

    exhibitions_queryset = Exhibition.get_active_objects().select_related('country').prefetch_related('organization')

    news_queryset = News.get_active_objects() \
        .select_related('country').prefetch_related('organization', 'organization__countries')

    def get(self, *args, **kwargs):
        return Response({
            'content': {
                'products': B2BProductSerializer(self.get_content(self.products_queryset, 4), many=True).data,
                'projects': ProjectsSerializer(self.get_content(self.projects_queryset, 1), many=True).data,
                'exhibitions': ExhibitionsSerializer(self.get_content(self.exhibitions_queryset, 1), many=True).data,
                'proposals': ProposalsSerializer(self.get_content(self.proposals_queryset, 1), many=True).data,
                'news': NewsSerializer(self.get_content(self.news_queryset, 1), many=True).data
            }.update(self.get_filter_data())
        })

    def get_content(self, queryset, count):
        s = SearchEngine(doc_type=queryset.model.get_index_model())

        for backend in self.filters:
            s = backend().filter_queryset(self.request, s, view=self)

        results = s.sort(*self.sorting).execute().hits[:count]

        return list(queryset.filter(pk__in=[hit.django_id for hit in results]).all())


class NewsList(BaseListApi):
    serializer_class = NewsSerializer
    queryset = News.get_active_objects() \
        .select_related('country').prefetch_related('organization', 'organization__countries')


class B2BProductList(BaseListApi):
    serializer_class = B2BProductSerializer
    queryset = B2BProduct.get_active_objects().prefetch_related('company__countries')


class B2CProductList(BaseListApi):
    serializer_class = B2CProductSerializer
    queryset = B2CProduct.get_active_objects().prefetch_related('company__countries')


class CouponList(BaseListApi):
    serializer_class = CouponSerializer
    queryset = Coupon.get_active_objects().prefetch_related('company__countries')
    is_filterable = False


class ProjectList(BaseListApi):
    serializer_class = ProjectsSerializer
    queryset = InnovationProject.get_active_objects().prefetch_related('organization', 'organization__countries')


class ProposalList(BaseListApi):
    serializer_class = ProposalsSerializer
    queryset = BusinessProposal.get_active_objects() \
        .prefetch_related('branches', 'organization', 'organization__countries')


class ExhibitionList(BaseListApi):
    serializer_class = ExhibitionsSerializer
    queryset = Exhibition.get_active_objects() \
        .select_related('country').prefetch_related('organization')


class CompanyList(BaseListApi):
    serializer_class = CompanySerializer
    queryset = Company.get_active_objects().prefetch_related('countries', 'parent')


class ChamberList(BaseListApi):
    serializer_class = ChamberSerializer
    queryset = Chamber.get_active_objects().select_related('parent').prefetch_related('countries')


class VideosList(BaseListApi):
    serializer_class = VideoSerializer
    queryset = VideoChannel.get_active_objects() \
        .select_related('country').prefetch_related('organization', 'organization__countries')


class VacancyList(BaseListApi):
    serializer_class = VacancySerializer
    queryset = Requirement.get_active_objects().select_related('country')


class ResumeList(BaseListApi):
    serializer_class = ResumeSerializer
    queryset = Resume.get_active_objects().select_related('user', 'user__profile', 'user__profile__country')


class Banners(BaseAdvertisementView):
    def get(self, *args, **kwargs):
        data = {}
        blocks = self.request.query_params.get('blocks', None)

        if not blocks:
            return Response(status=400)

        for block in blocks.split(','):
            banner = func.get_banner(block, None, self.list_adv_filter)

            if not banner:
                continue

            data[block] = BannerSerializer(instance=banner).data

        return Response(data)


class ContextAdvertisements(BaseAdvertisementView):
    def get(self, *args, **kwargs):
        result = {}

        tops = func.get_tops(self.list_adv_filter) or {}

        for data in tops.values():
            items = data['queryset'].all()

            if len(items) == 0:
                continue

            result[data['key']] = ContextAdvertisementSerializer(data['queryset'].all(), many=True).data

        return Response(result)
