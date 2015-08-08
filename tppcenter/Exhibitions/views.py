from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import trans_real, ugettext as _
from django.utils.timezone import now

from appl.models import AdditionalPages, Gallery, Organization, Branch, Country
from appl import func
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import Exhibition
from core.models import Item
from core.tasks import addNewExhibition
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class ExhibitionList(ItemsList):
    #pagination url
    url_paginator = "exhibitions:paginator"
    url_my_paginator = "exhibitions:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Exhibitions")
    addUrl = 'exhibitions:add'

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = Exhibition

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Exhibitions/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Exhibitions/index.html'

    def get_queryset(self):
        queryset = super(ExhibitionList, self).get_queryset()
        return queryset.select_related('country').prefetch_related('organization')


class ExhibitionDetail(ItemDetail):
    model = Exhibition
    template_name = 'Exhibitions/detailContent.html'

    current_section = _("Exhibitions")
    addUrl = 'exhibitions:add'


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
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)
    pages = None

    countries = func.getItemsList("Country", 'NAME')
    choosen_country = int(request.POST.get('COUNTRY', 0))

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
    context = RequestContext(request,  {'form': form, 'branches': branches, 'pages': pages, 'countries': countries, 'choosen_country': choosen_country})
    exhibitionPage = template.render(context)

    return exhibitionPage


def updateExhibition(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'change_exhibition' not in perm_list:
        return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
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

    countries = func.getItemsList("Country", 'NAME')
    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id).pk
    except ObjectDoesNotExist:
        choosen_country = ""


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
        'branches': branches,
        'countries': countries,
        'choosen_country': choosen_country
    }

    context = RequestContext(request, templateParams)
    exhibitionPage = template.render(context)

    return exhibitionPage


def deleteExhibition(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_exhibition' not in perm_list:
        return func.permissionDenied()

    instance = Exhibition.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('exhibitions:main'))



