from urllib.parse import urlparse
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import Truncator
from django.utils.translation import gettext as _
from django.template import loader, RequestContext
from django.views.generic import DetailView
from haystack.backends import SQ
from haystack.query import SearchQuerySet

from appl import func
from appl.models import Country, AdditionalPages, Gallery, Company, Tpp
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

    #sorting fields
    sortField1 = 'date'
    sortField2 = None
    order1 = 'desc'
    order2 = None

    #Queryset taken from db not indexes
    querysetDB = False

    #current page
    page = 1

    #Add namespace
    addUrl = ''

    #Section name
    current_section = ''

    #pagination url
    url_paginator = None
    url_my_paginator = None

    url_parameter = []


    #Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    #Fields to sort by
    sortFields = {
        'date': 'obj_create_date',
        'name': 'title_sort'
    }

    #Applied filters
    filters = {}

    #My tab selected
    my = False

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch', 'bp_category']

    def _get_countrys_for_objects(self, object_list):

        countries = []

        for obj in object_list:
            country = getattr(obj, 'country', False)

            if not country:
                continue

            if isinstance(country, list):
                if len(country) != 1:
                    continue
                else:
                    country = country[0]

            countries.append(country)

        if len(countries) > 0:
            countryDict = {}
            new_object_list = []

            for country in SearchQuerySet().models(Country).filter(django_id__in=countries):
                countryDict[int(country.pk)] = country

            if len(countryDict) > 0:
                for obj in object_list:
                    country = getattr(obj, 'country', None)

                    if not country:
                        new_object_list.append(obj)
                        continue

                    if isinstance(country, list):
                        if len(country) == 1:
                            country = int(country[0])
                        else:
                            new_object_list.append(obj)
                            continue

                    if country not in countryDict:
                        new_object_list.append(obj)
                        continue

                    obj.country = countryDict[int(country)]
                    new_object_list.append(obj)

                return new_object_list

        return object_list


    def _get_organization_for_objects(self, object_list):

        orgs = []

        for obj in object_list:

            company = getattr(obj, 'company', False)
            tpp = getattr(obj, 'tpp', False)

            if company:
                orgs.append(company)
            elif tpp:
                orgs.append(tpp)

        if len(orgs) > 0:
            orgDict = {}

            for org in SearchQuerySet().models(Company, Tpp).filter(django_id__in=orgs):
                orgDict[int(org.pk)] = org

            if len(orgDict) > 0:
                new_object_list = []

                for obj in object_list:
                    company = getattr(obj, 'company', False)
                    tpp = getattr(obj, 'tpp', False)

                    if company:
                        if company in orgDict:
                            orgDict[company].__setattr__('url', 'companies:detail')
                            obj.__setattr__('organization', orgDict[company])
                    elif tpp:
                        if tpp in orgDict:
                            orgDict[tpp].__setattr__('url', 'tpp:detail')
                            obj.__setattr__('organization', orgDict[tpp])

                    new_object_list.append(obj)

                return new_object_list

        return object_list

    def _get_items_perms(self, object_list):
        if self.request.user.is_authenticated():
            item_ids = [obj.pk for obj in object_list]
            return func.getUserPermsForObjectsList(self.request.user, item_ids, self.model.__name__)

        return None

    def get_data(self, context):
        #For JSON response
        template = loader.get_template(self.template_name)
        context = RequestContext(self.request, context)

        return {
            'styles': self.styles,
            'scripts': self.scripts,
            'content': template.render(context),
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
            'current_section': self.current_section
        }

    def get_context_data(self, **kwargs):
        context = super(ItemsList, self).get_context_data(**kwargs)

        if self.querysetDB:
            ids = [obj.pk for obj in context['object_list']]
            context['object_list'] = SearchQuerySet().models(self.model).filter(django_id__in=ids)

        context['object_list'] = self._get_countrys_for_objects(context['object_list'])
        context['object_list'] = self._get_organization_for_objects(context['object_list'])

        context.update({
            'filters': self.filters,
            'sortField1': self.sortField1,
            'sortField2': self.sortField2,
            'order1': self.order1,
            'order2': self.order2,
            'page': context['page_obj'],
            'paginator_range': func.getPaginatorRange(context['page_obj']),
            'url_parameter': self.url_parameter,
            'url_paginator': self.url_my_paginator if self.is_my() else self.url_paginator,
            'items_perms': self._get_items_perms(context['object_list']),
            'current_path': self.request.get_full_path(),
            'addNew': '' if not self.addUrl else reverse(self.addUrl),
            'current_section': self.current_section,
            'styles': self.styles,
            'scripts': self.scripts,
            'model': self.model.__name__
        })

        return context

    def is_my(self):
        return self.my

    def ajax(self, request, *args, **kwargs):
        pass

    def no_ajax(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):

        if request.is_ajax():
            self.ajax(request, *args, **kwargs)
        else:
            self.no_ajax(request, *args, **kwargs)

        return super(ItemsList, self).get(request, *args, **kwargs)


    def filterLive(self):
        '''
            Converting request GET filter parameters (from popup window) to filter parameter for SearchQuerySet filter

            obj request - request context
        '''

        #session_key_model_name = 'filter_' + self.model.__name__.lower()

        filtersIDs = {}
        ids = []

        #get all filter parameters from request GET
        for name in self.filterList:
            filtersIDs[name] = []
            self.filters[name] = []

            for pk in self.request.GET.getlist('filter[' + name + '][]', []):
                try:
                    filtersIDs[name].append(int(pk))
                except ValueError:
                    continue

            ids += filtersIDs[name]

        #Do we have any valid filter ?
        if len(ids) > 0:
            items = SearchQuerySet().filter(django_id__in=ids)

            for item in items:
                #Creating a list of filter parameters

                for name, id in filtersIDs.items():

                    if int(item.pk) in id:
                        self.filters[name].append({'id': item.pk, 'text': item.title_auto})


        searchFilter = self._create_sqs_filter()

        if len(searchFilter) > 0: #Converting a list of filter parameters to big "OR" filter

            #self.request.session[session_key_model_name] = self.filters
            return eval(' | '.join(searchFilter))
        '''
        elif len(self.request.session.get(session_key_model_name, {})) > 0:
            self.filters = self.request.session.get(session_key_model_name, {})
            searchFilter = self._create_sqs_filter()

            return eval(' | '.join(searchFilter))
        '''
        return None

    def _create_sqs_filter(self):

        newIDs = []
        searchFilter = []

        for name, filterList in self.filters.items():

            for filter in filterList:
                try:
                    #Security
                    newIDs.append(str(int(filter['id'])))
                except ValueError:
                    continue

            if len(newIDs) > 0:
                searchFilter.append('SQ(' + name + '__in =[' + ','.join(newIDs) + '])')

        return searchFilter

    def _get_sorting_params(self):
        order = []

        self.sortField1 = self.request.GET.get('sortField1', 'obj_create_date')
        self.sortField2 = self.request.GET.get('sortField2', None)
        self.order1 = self.request.GET.get('order1', 'desc')
        self.order2 = self.request.GET.get('order2', None)

        if self.sortField1 and self.sortField1 in self.sortFields:
            if self.order1 == 'desc':
                order.append('-' + self.sortFields[self.sortField1])
            else:
                order.append(self.sortFields[self.sortField1])
        else:
            order.append('-obj_create_date')

        if self.sortField2 and self.sortField2 in self.sortFields:
            if self.order2 == 'desc':
                order.append('-' + self.sortFields[self.sortField2])
            else:
                order.append(self.sortFields[self.sortField2])

        return order

    def _get_my(self):
        current_organization = self.request.session.get('current_company', False)

        if current_organization is False:
            if self.request.is_ajax():
                self.template_name = 'permissionDen.html'
            else:
                self.template_name = 'main/denied.html'

            return SQ(django_id=0)

        return SQ(tpp=current_organization) | SQ(company=current_organization)


    def get_queryset(self):

        sqs = func.getActiveSQS().models(self.model)

        if self.request.user.is_authenticated() and self.is_my():
            sqs = sqs.filter(self._get_my())
        else:
            searchFilter = self.filterLive()

            if searchFilter:
                sqs = sqs.filter(searchFilter)


        q = self.request.GET.get('q', '').strip()

        if q != '': #Search for content
            sqs = sqs.filter(SQ(title=q) | SQ(text=q))

        return sqs.order_by(*self._get_sorting_params())


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