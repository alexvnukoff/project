from appl.models import Tender, Gallery, AdditionalPages, Organization
from appl import func
from core.tasks import addNewTender
from core.models import Dictionary, Item
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.forms.models import modelformset_factory
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _, trans_real
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
import json

def get_tenders_list(request, page=1, item_id=None, my=None, slug=None):


   # if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('tenders:detail',  args=[slug]))


    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    if item_id is None:
        try:
            attr = ('NAME', 'COST', 'CURRENCY', 'SLUG')
            tendersPage = func.setContent(request, Tender, attr, 'tenders', 'Tenders/contentPage.html', 5, page=page,
                                          my=my)
        except ObjectDoesNotExist:
            tendersPage = func.emptyCompany()
    else:
        tendersPage, meta = _tenderDetailContent(request, item_id)

    if not request.is_ajax():
        current_section = _("Tenders")

        templateParams =  {
            'current_section': current_section,
            'tendersPage': tendersPage,
            'scripts': scripts,
            'styles': styles,
            'addNew': reverse('tenders:add'),
            'item_id': item_id
        }

        if item_id:
            templateParams['meta'] = meta

        return render_to_response("Tenders/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': tendersPage,
        }

        return HttpResponse(json.dumps(serialize))





def _tenderDetailContent(request, item_id):

    lang = settings.LANGUAGE_CODE
    cache_name = "%s_detail_%s" % (lang, item_id)

    cached = cache.get(cache_name)

    if not cached:

         tender = get_object_or_404(Tender, pk=item_id)

         attr = (
             'NAME', 'COST', 'CURRENCY', 'START_EVENT_DATE', 'END_EVENT_DATE',
            'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'DETAIL_TEXT'
         )

         tenderValues = tender.getAttributeValues(*attr)

         photos = Gallery.objects.filter(c2p__parent=item_id)

         additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

         func.addToItemDictinoryWithCountryAndOrganization(tender.id, tenderValues)

         template = loader.get_template('Tenders/detailContent.html')

         templateParams = {
            'tenderValues': tenderValues,
            'photos': photos,
            'additionalPages': additionalPages,
            'item_id': item_id
         }

         context = RequestContext(request, templateParams)
         rendered = template.render(context)

         meta = func.getItemMeta(request, tenderValues)

         cache.set(cache_name, [rendered, meta], 60*60*24*7)

    else:
        rendered, meta = cache.get(cache_name)

    return rendered, meta



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

    item = Organization.objects.get(p2c__child_id=item_id)

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
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_tender' not in perm_list:
        return func.permissionDenied()

    instance = Tender.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('tenders:main'))



