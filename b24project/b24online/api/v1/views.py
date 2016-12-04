from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

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

    products_queryset = B2BProduct.get_active_objects()
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
    news = ContentHelper(queryset=news_queryset, request=request, page_size=10)

    return Response({'content': NewsSerializer(news.content, many=True).data})
