from urllib.parse import urlparse

from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import Truncator
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from haystack.query import SearchQuerySet

from appl import func
from appl.models import Country, AdditionalPages, Gallery
from core.cbv import HybridListView
from tpp import settings


class TabItemList(HybridListView):
    paginate_by = 10
    allow_empty = True

    #pagination url
    url_paginator = None


class ItemsList(HybridListView):

    paginate_by = 10
    #context_object_name = 'items'
    allow_empty = True

    #current page
    page = 1

    #pagination url
    url_paginator = None
    url_my_paginator = None

    url_parameter = []

    category = None

    def _get_favorites(self, object_list):
        if self.request.user.is_authenticated():
            obj_ids = [obj.pk for obj in object_list]
            return list(
                Favorite.objects.filter(c2p__parent__cabinet__user=self.request.user, p2c__child__in=obj_ids)
                    .values_list("p2c__child", flat=True)
            )

        return []

    def get_queryset(self):

        sqs = func.getActiveSQS().models(self.model)

        self.category = self.kwargs.get('category', None)
        country = self.kwargs.get('country', None)

        if self.category:
            sqs = sqs.filter(categories=self.category)

        if country:
            sqs = sqs.filter(country=country)

        return sqs.order_by('-obj_create_date')


class ItemDetail(DetailView):
    context_object_name = 'item'
    item_id = None


    #Add namespace
    addUrl = ''

    #Section name
    current_section = ''

    def get_queryset(self):
        return func.getActiveSQS().models(self.model)

    def get_object(self, queryset=None):

        queryset = self.get_queryset()

        self.item_id = self.kwargs.get('item_id', None)
        slug = self.kwargs.get('slug', None)

        if self.item_id is not None:
            queryset = queryset.filter(django_id=self.item_id)
        elif slug is not None:
            queryset = queryset.filter(slug=slug)

        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        if queryset.count() == 0:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})

        return queryset[0]

    def _get_additional_pages(self):
        return AdditionalPages.objects.filter(c2p__parent=self.object.pk)

    def _get_country_for_object(self):

        country = getattr(self.object, 'country', None)

        if not country:
            return country

        if isinstance(country, list):
            if len(country) != 1:
                return country
            else:
                country = country[0]


        country = SearchQuerySet().models(Country).filter(django_id=country)

        if country.count() != 1:
            return None

        return country[0]

    def _get_organization_for_object(self):

        tpp = getattr(self.object, 'tpp', None)
        company = getattr(self.object, 'company', None)

        if company:

            company = SearchQuerySet().filter(django_id=company)[0]
            company.__setattr__('url', 'companies:detail')
            return company
        elif tpp:
            tpp = SearchQuerySet().filter(django_id=tpp)[0]
            tpp.__setattr__('url', 'tpp:detail')
            return tpp

        return None

    def _get_gallery(self):
        return Gallery.objects.filter(c2p__parent=self.object.pk)

    def _get_item_meta(self):

        image = ''

        if getattr(self.object, 'image', False):
            image = settings.MEDIA_URL + 'original/' + self.object.image

        url = urlparse(self.request.build_absolute_uri())

        title = self.object.title if getattr(self.object, 'title', False) else getattr(self.object, 'text', "")

        return {
            'title': Truncator(title).chars("80", truncate='...'),
            'image': image,
            'url': url.scheme + "://" + url.netloc + url.path,
            'text': getattr(self.object, 'text', "")
        }

    def get_context_data(self, **kwargs):
        context = super(ItemDetail, self).get_context_data(**kwargs)

        context[self.context_object_name].__setattr__('country', self._get_country_for_object())
        context[self.context_object_name].__setattr__('organization', self._get_organization_for_object())

        context.update({
            'item_id': self.item_id,
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
            'current_section': self.current_section,
            'meta': self._get_item_meta()
        })

        return context