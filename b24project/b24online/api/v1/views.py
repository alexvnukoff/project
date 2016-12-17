from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from b24online.api.v1.helpers import ContentHelper
from b24online.api.v1.serializers import B2BProductSerializer, ProjectsSerializer, ProposalsSerializer, \
    ExhibitionsSerializer, NewsSerializer, CompanySerializer, ChamberSerializer, B2CProductSerializer, CouponSerializer, \
    VideoSerializer, VacancySerializer, ResumeSerializer
from b24online.models import InnovationProject, B2BProduct, BusinessProposal, Exhibition, News, Company, Chamber, \
    VideoChannel
from centerpokupok.models import B2CProduct, Coupon
from jobs.models import Requirement, Resume


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def wall(request):
    projects_queryset = InnovationProject.get_active_objects() \
        .prefetch_related('organization', 'organization__countries')

    projects = ContentHelper(queryset=projects_queryset, request=request, page_size=1)

    products_queryset = B2BProduct.get_active_objects().prefetch_related('company__countries')
    products = ContentHelper(queryset=products_queryset, request=request, page_size=4)

    proposals_queryset = BusinessProposal.get_active_objects() \
        .prefetch_related('branches', 'organization', 'organization__countries')
    proposals = ContentHelper(queryset=proposals_queryset, request=request, page_size=1)

    exhibitions_queryset = Exhibition.get_active_objects().select_related('country').prefetch_related('organization')
    exhibitions = ContentHelper(request=request, queryset=exhibitions_queryset, page_size=1)

    news_queryset = News.get_active_objects() \
        .select_related('country').prefetch_related('organization', 'organization__countries')
    news = ContentHelper(queryset=news_queryset, request=request, page_size=1)

    return Response({'content': {
        'products': B2BProductSerializer(products.content, many=True).data,
        'projects': ProjectsSerializer(projects.content, many=True).data,
        'exhibitions': ExhibitionsSerializer(exhibitions.content, many=True).data,
        'proposals': ProposalsSerializer(proposals.content, many=True).data,
        'news': NewsSerializer(news.content, many=True).data
    }})


@api_view(['GET'])
def news(request):
    news_queryset = News.get_active_objects() \
        .select_related('country').prefetch_related('organization', 'organization__countries')
    serialized_news = ContentHelper(queryset=news_queryset, request=request, page_size=10)

    return Response({'content': NewsSerializer(serialized_news.content, many=True).data})


@api_view(['GET'])
def b2b_products(request):
    products_queryset = B2BProduct.get_active_objects().prefetch_related('company__countries')
    serialized_products = ContentHelper(queryset=products_queryset, request=request, page_size=10)

    return Response({'content': B2BProductSerializer(serialized_products.content, many=True).data})


@api_view(['GET'])
def b2c_products(request):
    products_queryset = B2CProduct.get_active_objects().prefetch_related('company__countries')
    serialized_products = ContentHelper(queryset=products_queryset, request=request, page_size=10)

    return Response({'content': B2CProductSerializer(serialized_products.content, many=True).data})


@api_view(['GET'])
def coupons(request):
    coupons_queryset = Coupon.get_active_objects().prefetch_related('company__countries')
    serialized_coupons = ContentHelper(queryset=coupons_queryset, request=request, page_size=10)

    return Response({'content': CouponSerializer(serialized_coupons.content, many=True).data})


@api_view(['GET'])
def projects(request):
    projects_queryset = InnovationProject.get_active_objects().prefetch_related('organization',
                                                                                'organization__countries')
    serialized_projects = ContentHelper(queryset=projects_queryset, request=request, page_size=10)

    return Response({'content': ProjectsSerializer(serialized_projects.content, many=True).data})


@api_view(['GET'])
def proposals(request):
    proposals_queryset = BusinessProposal.get_active_objects() \
        .prefetch_related('branches', 'organization', 'organization__countries')
    serialized_proposals = ContentHelper(queryset=proposals_queryset, request=request, page_size=10)

    return Response({'content': ProposalsSerializer(serialized_proposals.content, many=True).data})


@api_view(['GET'])
def exhibitions(request):
    exhibitions_queryset = Exhibition.get_active_objects() \
        .select_related('country').prefetch_related('organization')
    serialized_exhibitions = ContentHelper(queryset=exhibitions_queryset, request=request, page_size=10)

    return Response({'content': ExhibitionsSerializer(serialized_exhibitions.content, many=True).data})


@api_view(['GET'])
def companies(request):
    companies_queryset = Company.get_active_objects().prefetch_related('countries', 'parent')
    serialized_companies = ContentHelper(queryset=companies_queryset, request=request, page_size=10)

    return Response({'content': CompanySerializer(serialized_companies.content, many=True).data})


@api_view(['GET'])
def chambers(request):
    chambers_queryset = Chamber.get_active_objects().select_related('parent').prefetch_related('countries')
    serialized_chambers = ContentHelper(queryset=chambers_queryset, request=request, page_size=10)

    return Response({'content': ChamberSerializer(serialized_chambers.content, many=True).data})


@api_view(['GET'])
def videos(request):
    videos_queryset = VideoChannel.get_active_objects()\
        .select_related('country').prefetch_related('organization', 'organization__countries')
    serialized_videos = ContentHelper(queryset=videos_queryset, request=request, page_size=10)

    return Response({'content': VideoSerializer(serialized_videos.content, many=True).data})


@api_view(['GET'])
def vacancies(request):
    vacancies_queryset = Requirement.get_active_objects().select_related('country')
    serialized_vacancies = ContentHelper(queryset=vacancies_queryset, request=request, page_size=10)

    return Response({'content': VacancySerializer(serialized_vacancies.content, many=True).data})


@api_view(['GET'])
def resumes(request):
    resumes_queryset = Resume.get_active_objects().select_related('user', 'user__profile', 'user__profile__country')
    serialized_resumes = ContentHelper(queryset=resumes_queryset, request=request, page_size=10)

    return Response({'content': ResumeSerializer(serialized_resumes.content, many=True).data})



