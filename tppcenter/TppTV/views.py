from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.utils.timezone import now

from appl import func
from appl.models import TppTV
from tppcenter.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate
from b24online.models import News, Organization


class TVNewsLIst(ItemsList):

    #pagination url
    url_paginator = "tv:paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css',
        settings.STATIC_URL + 'tppcenter/css/tpp.reset.css'
    ]

    current_section = _("TPP-TV")

    #allowed filter list
    # filter_list = ['tpp', 'country', 'company']

    model = News

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated():

            if request.user.is_superuser or self._is_redactor():
                self.addUrl = 'tv:add'

        return super().dispatch(request, *args, **kwargs)

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'TppTV/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'TppTV/index.html'

    def _is_redactor(self):
        if 'Redactor' in self.request.user.groups.values_list('name', flat=True):
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super(TVNewsLIst, self).get_context_data(**kwargs)

        context['redactor'] = False

        if self.request.user.is_authenticated():
            context['redactor'] = self._is_redactor()

        return context

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization', 'organization__countries')

    def filter_search_object(self, s):
        return super().filter_search_object(s).query('match', is_tv=True)

    def get_queryset(self):
        queryset = super(TVNewsLIst, self).get_queryset()

        if self.is_filtered():
            return queryset

        return queryset.filter(is_tv=True)


class TVNewsDetail(ItemDetail):
    model = News
    template_name = 'TppTV/detailContent.html'

    current_section = _("TPP-TV")

    def get_queryset(self):
        return super().get_queryset().filter(is_tv=True)

    def _get_similar_news(self):
        if self.object.categories.exists():
            return News.objects.filter(is_tv=True, categories__in=self.object.categories.all()) \
                .order_by('-created_at')[:3]

        return News.objects.filter(is_tv=True, categories=None).order_by('-created_at')[:3]


    def get_context_data(self, **kwargs):
        context = super(TVNewsDetail, self).get_context_data(**kwargs)
        context['similarNews'] = self._get_similar_news()

        return context


@login_required
def tvForm(request, action, item_id=None):
    if item_id:
       if not TppTV.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("TppTv")
    newsPage = ''

    if action == 'delete':
        newsPage = deleteTppTv(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

@login_required
def deleteTppTv(request, item_id):

    if not 'Redactor' in request.user.groups.values_list('name', flat=True):
        return func.permissionDenied()

    instance = TppTV.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('tv:main'))


class TvCreate(ItemCreate):
    org_required = False
    model = News
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'TppTV/addForm.html'
    success_url = reverse_lazy('tv:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.is_tv = True
        organization_id = self.request.session.get('current_company', None)

        if organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
            form.instance.organization = organization
            form.instance.country = organization.country

        result = super().form_valid(form)
        self.object.reindex()
        self.object.upload_images()

        return result


class TvUpdate(ItemUpdate):
    model = News
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'TppTV/addForm.html'
    success_url = reverse_lazy('tv:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        organization_id = self.request.session.get('current_company', None)

        if organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
            form.instance.organization = organization
            form.instance.country = organization.country

        result = super().form_valid(form)

        if form.changed_data:
            self.object.reindex()

            if 'image' in form.changed_data:
                self.object.upload_images()

        return result