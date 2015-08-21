from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.forms.models import modelformset_factory
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.timezone import now
from django.utils.translation import ugettext as _, trans_real

from appl.models import Gallery, AdditionalPages, Organization
from appl import func
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Tender
from core.tasks import addNewTender
from core.models import Dictionary
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class TenderList(ItemsList):
    #pagination url
    url_paginator = "tenders:paginator"
    url_my_paginator = "tenders:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Tenders")
    addUrl = 'tenders:add'

    #allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    model = Tender

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Tenders/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Tenders/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization')

    def get_queryset(self):
        queryset = super(TenderList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class TenderDetail(ItemDetail):
    model = Tender
    template_name = 'Tenders/detailContent.html'

    current_section = _("Tenders")
    addUrl = 'tenders:add'


@login_required(login_url='/login/')
def tenderForm(request, action, item_id=None):
    if item_id:
       if not Tender.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Tenders")
    tendersPage = ''

    if action == 'delete':
        tendersPage = deleteTender(request, item_id)
    elif action == 'add':
        tendersPage = addTender(request)
    elif action == 'update':
        tendersPage = updateTender(request, item_id)

    if isinstance(tendersPage, HttpResponseRedirect) or isinstance(tendersPage, HttpResponse):
        return tendersPage

    templateParams = {
        'formContent': tendersPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

def addTender(request):

    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_tender' not in perm_list:
         return func.permissionDenied()

    form = None
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()
    pages = None
    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
            pages = pages.new_objects


        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Tender', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTender.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company,
                               lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('tenders:main'))

    template = loader.get_template('Tenders/addForm.html')
    context = RequestContext(request, {'form': form, 'currency_slots': currency_slots, 'pages': pages})
    tendersPage = template.render(context)

    return tendersPage


def updateTender(request, item_id):

    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_tender' not in perm_list:
        return func.permissionDenied()

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()


    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)
    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

    form = ItemForm('Tender', id=item_id)

    if request.POST:
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Tender', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewTender.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                               lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('tenders:main'))

    template = loader.get_template('Tenders/addForm.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'currency_slots': currency_slots,
        'pages': pages
    }

    context = RequestContext(request, templateParams)
    tendersPage = template.render(context)

    return tendersPage



def deleteTender(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_tender' not in perm_list:
        return func.permissionDenied()

    instance = Tender.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('tenders:main'))



