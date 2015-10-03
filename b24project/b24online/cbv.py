import os
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils._os import abspathu
from django.utils.decorators import method_decorator
from django.utils.text import Truncator
from django.views.generic import UpdateView, DetailView, CreateView, DeleteView, ListView

from appl import func
from b24online.models import Organization, Country, B2BProductCategory, Branch, BusinessProposalCategory, Gallery, \
    GalleryImage, Document
from b24online.search_indexes import SearchEngine
from core import tasks
from core.cbv import HybridListView
from b24online.forms import GalleryImageForm, DocumentForm


class TabItemList(HybridListView):
    paginate_by = 10
    allow_empty = True

    #pagination url
    url_paginator = None


class ItemUpdate(UpdateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if not obj.has_perm(request.user):
            return HttpResponseRedirect(reverse('denied'))

        return super().dispatch(request, *args, **kwargs)


class ItemDeactivate(DeleteView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if not obj.has_perm(request.user):
            return HttpResponseRedirect(reverse('denied'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def reindex_kwargs(self):
        return {}

    def get_success_url(self):
        return self.request.GET.get('next')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        self.object.reindex(is_active_changed=True)

        return HttpResponseRedirect(success_url)


class ItemCreate(CreateView):
    org_required = True
    org_model = Organization

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        organization_id = self.request.session.get('current_company', None)

        if not organization_id and self.org_required:
            return HttpResponseRedirect(reverse('denied'))
        elif organization_id:
            try:
                organizations = self.org_model.objects.get(pk=organization_id)

                if not organizations.has_perm(request.user):
                    return HttpResponseRedirect(reverse('denied'))
            except ObjectDoesNotExist:
                if self.org_required:
                    return HttpResponseRedirect(reverse('denied'))

        return super().dispatch(request, *args, **kwargs)


class ItemsList(HybridListView):
    paginate_by = 10
    allow_empty = True

    # Sorting fields
    sortField1 = 'date'
    sortField2 = None
    order1 = 'desc'
    order2 = None

    # Queryset taken from db not indexes
    querysetDB = False

    # Current page
    page = 1

    # Add namespace
    addUrl = ''

    # Section name
    current_section = ''

    # Pagination url
    url_paginator = None
    url_my_paginator = None

    url_parameter = []

    # Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    # Fields to sort by
    sortFields = {
        'date': 'created_at',
        'name': 'name'
    }

    # My tab selected
    my = False

    # Allowed filter list
    filter_list = {
        'organization': Organization,
        'country': Country,
        'countries': Country,
        'b2b_categories': B2BProductCategory,
        'branches': Branch,
        'bp_categories': BusinessProposalCategory,
    }

    @classmethod
    def as_view(cls, **initkwargs):
        method = getattr(cls.model, 'get_index_model', None)

        if method is None:
            cls.filter_list = {}
        else:
            intersec = method()._doc_type.mapping.properties._params['properties'].keys() & cls.filter_list.keys()

            if not intersec:
                cls.filter_list = {}
            else:
                cls.filter_list = {k: cls.filter_list.get(k, None) for k in intersec}

        return super().as_view(**initkwargs)

    def dispatch(self, request, *args, **kwargs):
        self.applied_filters = {}

        return super().dispatch(request, *args, **kwargs)

    def is_filtered(self):
        q = self.request.GET.get('q', '').strip()
        return bool(self.applied_filters or q)

    def get_filtered_items(self):
        s = SearchEngine(doc_type=self.model.get_index_model())
        q = self.request.GET.get('q', '').strip()

        for filter_key in list(self.filter_list.keys()):
            filter_lookup = "filter[%s][]" % filter_key
            values = self.request.GET.getlist(filter_lookup)

            if values:
                s = s.filter('terms', **{filter_key: values})

        if q:
            s = s.query("multi_match", query=q, fields=['title', 'name', 'description', 'content'])

        return self.filter_search_object(s)

    def get_add_url(self):
        return self.addUrl

    def get_data(self, context):
        # For JSON response
        template = get_template(self.template_name)
        context = RequestContext(self.request, context)

        return {
            'styles': self.styles,
            'scripts': self.scripts,
            'content': template.render(context),
            'addNew': '' if not self.get_add_url() else reverse(self.get_add_url()),
        }

    def get_context_data(self, **kwargs):
        context = super(ItemsList, self).get_context_data(**kwargs)

        context.update({
            'applied_filters': self.applied_filters,
            'sortField1': self.sortField1,
            'sortField2': self.sortField2,
            'order1': self.order1,
            'order2': self.order2,
            'page': context['page_obj'],
            'paginator_range': func.get_paginator_range(context['page_obj']),
            'url_parameter': self.url_parameter,
            'url_paginator': self.url_my_paginator if self.is_my() else self.url_paginator,
            'items_perms': None,  # Deprecated
            'current_path': self.request.get_full_path(),
            'addNew': '' if not self.get_add_url() else reverse(self.get_add_url()),
            'current_section': self.current_section,
            'styles': self.styles,
            'scripts': self.scripts,
            'available_filters': list(self.filter_list.keys()),
            'model': self.model.__name__
        })

        if isinstance(context['object_list'], SearchEngine):
            object_ids = [hit.django_id for hit in context['object_list'].execute().hits]
            context['object_list'] = self.optimize_queryset(self.model.objects.filter(pk__in=object_ids))

        return context

    def ajax(self, request, *args, **kwargs):
        pass

    def no_ajax(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        for f, model in self.filter_list.items():
            key = "filter[%s][]" % f
            values = request.GET.getlist(key)

            if values:
                self.applied_filters[f] = model.objects.filter(pk__in=values).values('pk', 'name')

        if request.is_ajax():
            self.ajax(request, *args, **kwargs)
        else:
            self.no_ajax(request, *args, **kwargs)

        return super(ItemsList, self).get(request, *args, **kwargs)

    def _get_sorting_params(self):
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
            order.append(self.sortFields['date'])

        if self.sortField2 and self.sortField2 in self.sortFields:
            if self.order2 == 'desc':
                order.append('-' + self.sortFields[self.sortField2])
            else:
                order.append(self.sortFields[self.sortField2])

        return order

    @property
    def _current_organization(self):
        return self.request.session.get('current_company', None)

    def is_my(self):
        return self.request.user.is_authenticated() and not self.request.user.is_anonymous() and self.my

    def filter_search_object(self, s):
        return s.query('match', is_active=True).query('match', is_deleted=False)

    def optimize_queryset(self, queryset):
        return queryset

    def get_queryset(self):
        if self.is_filtered() and not self.is_my():
            return self.get_filtered_items().sort(*self._get_sorting_params())

        queryset = self.model.get_active_objects().filter(is_active=True).order_by(*self._get_sorting_params())
        return self.optimize_queryset(queryset)


class ItemDetail(DetailView):
    context_object_name = 'item'
    item_id = None

    # Add namespace
    addUrl = ''

    # Section name
    current_section = ''

    def get_add_url(self):
        return self.addUrl

    def get_queryset(self):
        return self.model.get_active_objects().all()

    def get_object(self, queryset=None):
        self.item_id = self.kwargs.get('item_id', None)
        # TODO: get by slug?

        if self.item_id:
            try:
                return self.get_queryset().get(pk=self.item_id)
            except ObjectDoesNotExist:
                raise Http404()
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

    def _get_item_meta(self):
        title = getattr(self.object, 'title', '') or getattr(self.object, 'name', '')
        image = settings.MEDIA_URL + 'original/' + self.object.image

        if image:
            getattr(self.object, 'logo', '') or getattr(self.object, 'image', '')

        url = urlparse(self.request.build_absolute_uri())

        return {
            'title': Truncator(title).chars("80", truncate='...'),
            'image': getattr(self.object, 'logo', '') or getattr(self.object, 'image', ''),
            'url': url.scheme + "://" + url.netloc + url.path,
            'text': getattr(self.object, 'description', "") or getattr(self.object, 'content', "")
        }
        pass

    def get_context_data(self, **kwargs):
        context = super(ItemDetail, self).get_context_data(**kwargs)

        context.update({
            'item_id': self.item_id,
            'addNew': '' if not self.get_add_url() else reverse(self.get_add_url()),
            'current_section': self.current_section,
            'meta': {}
        })

        return context


class GalleryImageList(ListView):
    model = GalleryImage
    owner_model = None
    context_object_name = 'gallery'
    paginate_by = 10
    is_structure = False
    page = 1
    namespace = None

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(self.owner_model, pk=kwargs['item'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.owner.galleries.exists():
            return self.owner.galleries.first().gallery_items.all()

        return self.model.objects.none()

    def get_uploader_url(self):
        return reverse("%s:tabs_gallery" % self.namespace, args=[self.owner.pk])

    def get_structure_url(self):
        return reverse("%s:gallery_structure" % self.namespace, args=[self.owner.pk, self.page])

    def get_remove_url(self):
        return "%s:gallery_remove_item" % self.namespace

    def get_paginator_url(self):
        return "%s:tabs_gallery_paged" % self.namespace

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            'page': context_data['page_obj'],
            'paginator_range': func.get_paginator_range(context_data['page_obj']),
            'url_paginator': self.get_paginator_url(),
            'has_perm': self.request.user.is_authenticated() and self.owner.has_perm(self.request.user),
            'item_id': self.owner.pk,
            'pageNum': self.page,
            'url_parameter': self.owner.pk,
            'uploaderURL': self.get_uploader_url(),
            'structureURL': self.get_structure_url(),
            'removeURL': self.get_remove_url()
        })

        return context_data

    def post(self, request, *args, **kwargs):
        return UploadGalleryImage.as_view()(request, self.owner)

    def get_template_names(self):
        if self.is_structure:
            return ['b24online/tab_gallery_structure.html']

        return ['b24online/tabGallery.html']


class UploadGalleryImage(CreateView):
    form_class = GalleryImageForm
    template_name = None

    def dispatch(self, request, owner, *args, **kwargs):
        self.owner = owner

        if not self.request.user.is_authenticated() or not self.owner.has_perm(self.request.user):
            return HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            model_type = ContentType.objects.get_for_model(self.owner)
            gallery, _ = Gallery.objects.get_or_create(content_type=model_type, object_id=self.owner.pk, defaults={
                'created_by': self.request.user,
                'updated_by': self.request.user
            })

            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user
            form.instance.gallery = gallery
            self.object = form.save()

        params = {
            'file': self.object.image.path,
            'sizes': {
                'big': {'box': (130, 120), 'fit': True}
            }
        }

        tasks.upload_images.apply((params,), {'async': True})

        return HttpResponse('')

    def form_invalid(self, form):
        return HttpResponseBadRequest()


class DeleteGalleryImage(ItemDeactivate):
    owner_model = None

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(self.owner_model, pk=kwargs['item'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.owner.galleries.all().first().gallery_items.all()

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return HttpResponse('')


class DocumentList(ListView):
    model = Document
    owner_model = None
    context_object_name = 'documents'
    paginate_by = 10
    is_structure = False
    page = 1
    namespace = None

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(self.owner_model, pk=kwargs['item'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.owner.documents.all()

    def get_uploader_url(self):
        return reverse("%s:tabs_documents" % self.namespace, args=[self.owner.pk])

    def get_structure_url(self):
        return reverse("%s:documents_structure" % self.namespace, args=[self.owner.pk, self.page])

    def get_remove_url(self):
        return "%s:documents_remove_item" % self.namespace

    def get_paginator_url(self):
        return "%s:tabs_documents_paged" % self.namespace

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data.update({
            'page': context_data['page_obj'],
            'paginator_range': func.get_paginator_range(context_data['page_obj']),
            'url_paginator': self.get_paginator_url(),
            'has_perm': self.request.user.is_authenticated() and self.owner.has_perm(self.request.user),
            'item_id': self.owner.pk,
            'pageNum': self.page,
            'url_parameter': self.owner.pk,
            'uploaderURL': self.get_uploader_url(),
            'structureURL': self.get_structure_url(),
            'removeURL': self.get_remove_url()
        })

        return context_data

    def post(self, request, *args, **kwargs):
        return UploadDocument.as_view()(request, self.owner)

    def get_template_names(self):
        if self.is_structure:
            return ['b24online/tab_documents_structure.html']

        return ['b24online/documents.html']


class UploadDocument(CreateView):
    form_class = DocumentForm
    template_name = None

    def dispatch(self, request, owner, *args, **kwargs):
        self.owner = owner

        if not self.request.user.is_authenticated() or not self.owner.has_perm(self.request.user):
            return HttpResponseBadRequest()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():

            form.instance.created_by = self.request.user
            form.instance.updated_by = self.request.user

            name = os.path.splitext(self.request.FILES['document'].name)[0]
            form.instance.name = name
            form.instance.item = self.owner
            self.object = form.save()

        abs_path = abspathu(settings.MEDIA_ROOT)
        path = self.object.document.path
        bucket_path = path[len(abs_path) + 1:] if abs_path in path else path

        params = {
            'file': path,
            'bucket_path': bucket_path
        }

        tasks.upload_file.apply((params,))

        return HttpResponse('')

    def form_invalid(self, form):
        return HttpResponseBadRequest()


class DeleteDocument(ItemDeactivate):
    owner_model = None

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(self.owner_model, pk=kwargs['item'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.owner.documents.all()

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return HttpResponse('')