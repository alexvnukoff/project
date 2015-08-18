from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, HttpResponse
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.utils.translation import trans_real

from appl import func
from appl.models import AdditionalPages, Organization, Branch, BpCategories
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import BusinessProposal, Gallery, Chamber, Country
from core.models import Item
from core.tasks import addBusinessPRoposal
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class BusinessProposalList(ItemsList):
    #pagination url
    url_paginator = "proposal:paginator"
    url_my_paginator = "proposal:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Business Proposal")
    addUrl = 'proposal:add'

    #allowed filter list
    filter_list = {
        'chamber': Chamber,
        'country': Country,
        'branch': Branch,
    }

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    model = BusinessProposal

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'BusinessProposal/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'BusinessProposal/index.html'

    def optimize_queryset(self, queryset):
        return queryset.prefetch_related('branches', 'organization', 'organization__countries')

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(organization_id=current_org)
            else:
                queryset = queryset.none()

        return queryset


class BusinessProposalDetail(ItemDetail):
    model = BusinessProposal
    template_name = 'BusinessProposal/detailContent.html'

    current_section = _("Business Proposal")
    addUrl = 'proposal:add'


@login_required(login_url='/login/')
def proposalForm(request, action, item_id=None):
    if item_id:
       if not BusinessProposal.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Business Proposal")

    if action == 'delete':
        proposalsPage = deleteProposal(request,item_id)
    elif action == 'add':
        proposalsPage = addBusinessProposal(request)
    elif action =='update':
        proposalsPage = updateBusinessProposal(request, item_id)

    if isinstance(proposalsPage, HttpResponseRedirect) or isinstance(proposalsPage, HttpResponse):
        return proposalsPage


    templateParams = {
        'formContent': proposalsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addBusinessProposal(request):
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_company)

    perm_list = item.getItemInstPermList(request.user)

    if 'add_businessproposal' not in perm_list:
         return func.permissionDenied()

    form = None

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    categories = BpCategories.objects.all()
    categories_id = [categorory.pk for categorory in categories]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

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
        branch = request.POST.get('BRANCH', "")

        form = ItemForm('BusinessProposal', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            addBusinessPRoposal.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch,
                                current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('proposal:main'))

    template = loader.get_template('BusinessProposal/addForm.html')

    context = RequestContext(request, {'form': form, 'branches': branches, 'pages': pages, 'categories': categories})

    proposalsPage = template.render(context)

    return  proposalsPage


def updateBusinessProposal(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
         photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

    perm_list = item.getItemInstPermList(request.user)

    if 'change_businessproposal' not in perm_list:
        return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.pk for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    categories = BpCategories.objects.all()
    categories_id = [categorory.pk for categorory in categories]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

    try:
        currentBranch = Branch.objects.get(p2c__child=item_id)
    except Exception:
        currentBranch = ""

    try:
        currentCategory = BpCategories.objects.get(p2c__child=item_id)
    except Exception:
        currentCategory = ""

    if request.method != 'POST':
        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages", parent_id=item_id)

        if getattr(pages, 'new_objects', False):
             pages = pages.new_objects
        else:
             pages = pages.queryset



        form = ItemForm('BusinessProposal', id=item_id)

    if request.POST:

        pages = ""

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)
        gallery.clean()



        values = {}
        values.update(request.POST)
        values.update(request.FILES)


        branch = request.POST.get('BRANCH', "")

        form = ItemForm('BusinessProposal', values=values, id=item_id)
        form.clean()


        if gallery.is_valid() and form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            addBusinessPRoposal.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, branch=branch,
                                lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('proposal:main'))



    template = loader.get_template('BusinessProposal/addForm.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'pages': pages,
        'currentBranch': currentBranch,
        'branches': branches,
        'currentCategory': currentCategory,
        'categories': categories,
    }

    context = RequestContext(request, templateParams)

    proposalsPage = template.render(context)

    return proposalsPage



def deleteProposal(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_businessproposal' not in perm_list:
        return func.permissionDenied()

    instance = BusinessProposal.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('proposal:main'))


