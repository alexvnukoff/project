from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from b24online.api.v1.helpers import ContentHelper
from b24online.api.v1.serializers import B2BProductSerializer, ProjectsSerializer, ProposalsSerializer, \
    ExhibitionsSerializer, NewsSerializer
from b24online.models import InnovationProject, B2BProduct, BusinessProposal, Exhibition, News


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
def products(request):
    products_queryset = B2BProduct.get_active_objects().prefetch_related('company__countries')
    serialized_products = ContentHelper(queryset=products_queryset, request=request, page_size=10)

    return Response({'content': B2BProductSerializer(serialized_products.content, many=True).data})


@api_view(['GET'])
def projects(request):
    projects_queryset = InnovationProject.get_active_objects().prefetch_related('organization', 'organization__countries')
    serialized_projects = ContentHelper(queryset=projects_queryset, request=request, page_size=10)

    return Response({'content': ProjectsSerializer(serialized_projects.content, many=True).data})


@api_view(['GET'])
def proposals(request):
    proposals_queryset = BusinessProposal.get_active_objects()\
        .prefetch_related('branches', 'organization', 'organization__countries')
    serialized_proposals = ContentHelper(queryset=proposals_queryset, request=request, page_size=10)

    return Response({'content': ProposalsSerializer(serialized_proposals.content, many=True).data})


@api_view(['GET'])
def exhibitions(request):
    exhibitions_queryset = Exhibition.get_active_objects()\
        .select_related('country').prefetch_related('organization')
    serialized_exhibitions = ContentHelper(queryset=exhibitions_queryset, request=request, page_size=10)

    return Response({'content': ExhibitionsSerializer(serialized_exhibitions.content, many=True).data})
