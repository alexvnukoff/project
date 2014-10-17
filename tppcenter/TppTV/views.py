from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _, trans_real
from django.utils.timezone import now
from haystack.query import SearchQuerySet

from appl import func
from appl.models import TppTV, NewsCategories, Country
from core.tasks import addTppAttrubute
from tppcenter.cbv import ItemDetail, ItemsList
from tppcenter.forms import ItemForm


class get_news_list(ItemsList):

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
    filterList = ['tpp', 'country', 'company']

    model = TppTV

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
        context = super(get_news_list, self).get_context_data(**kwargs)

        context['redactor'] = False

        if self.request.user.is_authenticated():
            context['redactor'] = self._is_redactor()

        return context



class get_news_detail(ItemDetail):

    model = TppTV
    template_name = 'TppTV/detailContent.html'

    current_section = _("TPP-TV")

    def _get_similar_news(self):
        categories = [category.pk for category in self.object.categories][:4]
        return SearchQuerySet().models(TppTV).filter(categories__in=categories)

    def _get_categories_for_object(self):
        return SearchQuerySet().filter(django_id__in=self.object.categories)

    def get_context_data(self, **kwargs):
        context = super(get_news_detail, self).get_context_data(**kwargs)
        context[self.context_object_name].__setattr__('categories', self._get_categories_for_object())

        context.update({
            'photos': self._get_gallery(),
            'similarNews': self._get_similar_news()
        })

        return context



@login_required(login_url='/login/')
def tvForm(request, action, item_id=None):
    if item_id:
       if not TppTV.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("TppTv")
    newsPage = ''

    if action == 'delete':
        newsPage = deleteTppTv(request, item_id)
    elif action == 'add':
        newsPage = addNews(request)
    elif action == 'update':
        newsPage = updateNew(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def addNews(request):

    perm = request.user.get_all_permissions()

    if not {'appl.add_tpptv'}.issubset(perm):
         return func.permissionDenied()

    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')


    if request.POST:
        user = request.user

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('TppTV', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=trans_real.get_language())
            return HttpResponseRedirect(reverse('tv:main'))

    template = loader.get_template('TppTV/addForm.html')
    context = RequestContext(request, {'form': form, 'categories': categories, 'countries': countries})
    newsPage = template.render(context)

    return newsPage


@login_required(login_url='/login/')
def updateNew(request, item_id):

    if not request.user.has_perm('appl.change_tpptv') or not request.user.groups.filter(name="Redactor").exists():
          return func.permissionDenied()

    create_date = TppTV.objects.get(pk=item_id).create_date

    try:
        choosen_category = NewsCategories.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    try:
        choosen_country = Country.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""

    countries = func.getItemsList("Country", 'NAME')
    categories = func.getItemsList('NewsCategories', 'NAME')

    if request.method != 'POST':
        form = ItemForm('TppTV', id=item_id)

    if request.POST:
        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('TppTV', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                  lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('tv:main'))


    template = loader.get_template('TppTV/addForm.html')

    templateParams = {
        'form': form,
        'choosen_category': choosen_category,
        'categories': categories,
        'create_date': create_date,
        'choosen_country':choosen_country,
        'countries': countries
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage


@login_required(login_url='/login/')
def deleteTppTv(request, item_id):

    if not 'Redactor' in request.user.groups.values_list('name', flat=True):
        return func.permissionDenied()

    instance = TppTV.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('tv:main'))
