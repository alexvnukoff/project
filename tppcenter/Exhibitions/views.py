from appl.models import Exhibition, AdditionalPages, Gallery, Organization, Branch
from appl import func
from core.models import Item
from core.tasks import addNewExhibition
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import trans_real, ugettext as _
from django.utils.timezone import now
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
import json

def get_exhibitions_list(request, page=1, item_id=None, my=None, slug=None):
    #if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #  slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      # return HttpResponseRedirect(reverse('exhibitions:detail',  args=[slug]))
    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    scripts = []
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    if not item_id:
        try:
            attr = ('NAME', 'CITY', 'COUNTRY', 'START_EVENT_DATE', 'END_EVENT_DATE', 'SLUG')
            exhibitionPage = func.setContent(request, Exhibition, attr, 'exhibitions', 'Exhibitions/contentPage.html',
                                             5, page=page, my=my)

        except ObjectDoesNotExist:
            exhibitionPage = func.emptyCompany()
    else:
        exhibitionPage, meta = _exhibitionsDetailContent(request, item_id)

    if not request.is_ajax():

        current_section = _("Exhibitions")

        templateParams = {
            'current_section': current_section,
            'exhibitionPage': exhibitionPage,
            'styles': styles,
            'scripts': scripts,
            'addNew': reverse('exhibitions:add'),
            'item_id': item_id
        }

        if item_id:
            templateParams['meta'] = meta

        return render_to_response("Exhibitions/index.html", templateParams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': exhibitionPage
        }

        return HttpResponse(json.dumps(serialize))


def _exhibitionsDetailContent(request, item_id):

    lang = settings.LANGUAGE_CODE
    cache_name = "%s_detail_%s" % (lang, item_id)
    cached = cache.get(cache_name)

    if not cached:

         exhibition = get_object_or_404(Exhibition, pk=item_id)

         attr = (
             'NAME', 'DETAIL_TEXT', 'START_EVENT_DATE',
             'END_EVENT_DATE', 'DOCUMENT_1', 'DOCUMENT_2',
             'DOCUMENT_3', 'CITY','ROUTE_DESCRIPTION', 'POSITION'
         )

         exhibitionlValues = exhibition.getAttributeValues(*attr)

         photos = Gallery.objects.filter(c2p__parent=item_id)

         additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)


         func.addToItemDictinoryWithCountryAndOrganization(exhibition.id, exhibitionlValues, withContacts=True)

         template = loader.get_template('Exhibitions/detailContent.html')

         templateParams = {
            'exhibitionlValues': exhibitionlValues,
            'photos': photos,
            'additionalPages': additionalPages,
            'item_id': item_id
         }

         context = RequestContext(request, templateParams)
         rendered = template.render(context)

         meta = func.getItemMeta(request, exhibitionlValues)

         cache.set(cache_name, [rendered, meta], 60*60*24*7)

    else:
        rendered, meta = cache.get(cache_name)

    return rendered, meta


@login_required(login_url='/login/')
def exhibitionForm(request, action, item_id=None):
    if item_id:
       if not Exhibition.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    current_section = _("Exhibitions")

    exhibitionPage = None

    if action == 'delete':
        exhibitionPage = deleteExhibition(request, item_id)
    elif action == 'add':
        exhibitionPage = addExhibition(request)
    elif action == 'update':
        exhibitionPage = updateExhibition(request, item_id)

    if isinstance(exhibitionPage, HttpResponseRedirect) or isinstance(exhibitionPage, HttpResponse):
        return exhibitionPage

    templateParams = {
        'formContent': exhibitionPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addExhibition(request):

    form = None
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_exhibition' not in perm_list:
         return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)
    pages = None

    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")
        if getattr(pages, 'new_objects', False):
           pages = pages.new_objects

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Exhibition', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewExhibition.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch,
                                   current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('exhibitions:main'))

    template = loader.get_template('Exhibitions/addForm.html')
    context = RequestContext(request,  {'form': form, 'branches': branches, 'pages': pages})
    exhibitionPage = template.render(context)

    return exhibitionPage


def updateExhibition(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_exhibition' not in perm_list:
        return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    try:
        currentBranch = Branch.objects.get(p2c__child=item_id)
    except Exception:
        currentBranch = ""

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)

    if getattr(pages, 'new_objects', False):
        pages = pages.new_objects
    else:
        pages = pages.queryset

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
        photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]


    form = ItemForm('Exhibition', id=item_id)

    if request.POST:
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)


        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('Exhibition', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewExhibition.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                   branch=branch, lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('exhibitions:main'))


    template = loader.get_template('Exhibitions/addForm.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'pages': pages,
        'currentBranch': currentBranch,
        'branches': branches
    }

    context = RequestContext(request, templateParams)
    exhibitionPage = template.render(context)

    return exhibitionPage


def deleteExhibition(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_exhibition' not in perm_list:
        return func.permissionDenied()

    instance = Exhibition.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('exhibitions:main'))



