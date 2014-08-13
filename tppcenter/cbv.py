import datetime
from django.utils import timezone
from haystack.backends import SQ
from haystack.query import SearchQuerySet
from appl import func
from core.cbv import HybridListView
from core.models import Item


class ItemsList(HybridListView):

    paginate_by = 10
    template_name = 'list.html'
    context_object_name = 'items'
    allow_empty = True

    #sorting fields
    sortField1 = 'date'
    sortField2 = None
    order1 = 'desc'
    order2 = None

    #current page
    page = 1

    #pagination url
    url_paginator = None
    url_parameter = None

    #fields to sort by
    sortFields = {
        'date': 'id',
        'name': 'title_sort'
    }

    #Applied filters
    filters = {}

    #My tab selected
    my = False

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch', 'bp_category']

    def get_context_data(self, **kwargs):
        context = super(ItemsList, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            item_ids = [obj.id for obj in context['object_list']]
            items_perms = func.getUserPermsForObjectsList(self.request.user, item_ids, self.model.__name__)
        else:
            items_perms = ""

        context.update({
            'filters': self.filters,
            'sortField1': self.sortField1,
            'sortField2': self.sortField2,
            'order1': self.order1,
            'order2': self.order2,
            'page': self.page,
            'paginator_range': func.getPaginatorRange(context['paginator']),
            'url_parameter': self.url_parameter,
            'url_paginator': self.url_paginator,
            'items_perms': items_perms,
            'current_path': self.request.get_full_path(),
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

        return self.render_to_response(self.get_context_data(), **kwargs)


    def filterLive(self):
        '''
            Converting request GET filter parameters (from popup window) to filter parameter for SearchQuerySet filter

            obj request - request context
        '''

        session_key_model_name = 'filter_' + self.model.__name__

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
            items = func.getActiveSQS().filter(id__in=ids)

            for item in items:
                #Creating a list of filter parameters

                for name, id in filtersIDs.items():

                    if item.id in id:
                        self.filters[name].append({'id': item.id, 'text': item.text})


        searchFilter = self._create_sqs_filter()

        if len(searchFilter) > 0: #Converting a list of filter parameters to big "OR" filter

            self.request.session[session_key_model_name] = self.filters
            return eval(' | '.join(searchFilter))

        elif len(self.request.session.get(session_key_model_name, {})) > 0:
            self.filters = self.request.session.get(session_key_model_name, {})
            searchFilter = self._create_sqs_filter()

            return eval(' | '.join(searchFilter))

        return None

    def _create_sqs_filter(self):

        newIDs = []
        searchFilter = []

        for name, filterList in self.filters.items():

            for filter in filterList:
                try:
                    #Security
                    newIDs.append(str(int(filter['pk'])))
                except ValueError:
                    continue

            if len(newIDs) > 0:
                searchFilter.append('SQ(' + name + '__in =[' + ','.join(newIDs) + '])')

        return searchFilter

    def _get_order(self):
        order = []

        self.sortField1 = self.request.GET.get('sortField1', 'date')
        self.sortField2 = self.request.GET.get('sortField2', None)
        self.order1 = self.request.GET.get('order1', 'desc')
        self.order2 = self.request.GET.get('order2', None)

        if self.sortField1 and self.sortField1 in self.sortFields:
            if self.order1 == 'desc':
                order.append('-' + self.sortFields[self.sortField1])
            else:
                order.append(self.sortFields[self.sortField1])
        else:
            order.append('-id')

        if self.sortField2 and self.sortField2 in self.sortFields:
            if self.order2 == 'desc':
                order.append('-' + self.sortFields[self.sortField2])
            else:
                order.append(self.sortFields[self.sortField2])

        return order

    def get_queryset(self):

        sqs = func.getActiveSQS().models(self.model)

        searchFilter = self.filterLive()

        if searchFilter:
            sqs.filter(searchFilter)


        q = self.request.GET.get('q', '')

        if q != '': #Search for content
            sqs = sqs.filter(SQ(title=q) | SQ(text=q))

        sqs.order_by(self._get_order())

        return sqs