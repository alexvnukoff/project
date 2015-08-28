from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.utils.timezone import now
from django.utils.translation import ugettext as _, trans_real

from appl import func
from appl.models import Branch, AdditionalPages, Cabinet, Gallery, Organization
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import InnovationProject
#from core.tasks import addNewProject
from core.models import Item, Dictionary
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class InnovationProjectList(ItemsList):
    # pagination url
    url_paginator = "innov:paginator"
    url_my_paginator = "innov:my_main_paginator"

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company', 'branch']

    model = InnovationProject

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('organization', 'organization__countries')

    def get_queryset(self):
        queryset = super(InnovationProjectList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(organization=current_org)
            else:
                queryset = self.model.objects.filter(created_by=self.request.user, organization__isnull=True)

        return queryset


class InnovationProjectDetail(ItemDetail):
    model = InnovationProject
    template_name = 'Innov/detailContent.html'

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    def get_queryset(self):
        return super().get_queryset() \
            .prefetch_related('galleries', 'galleries__gallery_items')


@login_required
def innovForm(request, action, item_id=None):
    if item_id:
        if not InnovationProject.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    current_section = _("Innovation Project")
    newsPage = ''

    if action == 'delete':
        newsPage = deleteInnov(request, item_id)
    elif action == 'add':
        newsPage = addProject(request)
    elif action == 'update':
        newsPage = updateProject(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'formContent': newsPage,
        'current_section': current_section
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addProject(request):
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
        return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_innovationproject' not in perm_list:
        return func.permissionDenied()

    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()
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

        form = ItemForm('InnovationProject', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            # addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch,
            #                     current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('innov:main'))

    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request,
                             {'form': form, 'branches': branches, 'currency_slots': currency_slots, 'pages': pages})
    newsPage = template.render(context)

    return newsPage


def updateProject(request, item_id):
    try:
        item = Organization.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        item = Cabinet.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)
    if 'change_innovationproject' not in perm_list:
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

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    form = ItemForm('InnovationProject', id=item_id)

    if request.POST:

        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        branch = request.POST.get('BRANCH', "")

        form = ItemForm('InnovationProject', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            # addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
            #                     branch=branch, lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('innov:main'))

    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form, 'pages': pages,
                                       'currentBranch': currentBranch, 'branches': branches,
                                       'currency_slots': currency_slots})
    newsPage = template.render(context)

    return newsPage


def deleteInnov(request, item_id):
    try:
        item = Organization.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        item = Cabinet.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_innovationproject' not in perm_list:
        return func.permissionDenied()

    instance = InnovationProject.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('innov:main'))
