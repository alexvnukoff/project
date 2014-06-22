from appl import func
from appl.models import BusinessProposal, Gallery, AdditionalPages, Organization, Branch, BpCategories
from core.models import Item
from core.tasks import addBusinessPRoposal
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, HttpResponse, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
from django.utils.translation import trans_real
import json

def get_proposals_list(request, page=1, item_id=None,  my=None, slug=None):
    #if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
     #    slug = Value.objects.get(item=item_id, attr__title='SLUG').title
      #   return HttpResponseRedirect(reverse('proposal:detail',  args=[slug]))
    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    description = ""
    title = ""

    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    if not item_id:
        try:
              proposalsPage = func.setContent(request, BusinessProposal, ('NAME', 'SLUG'), 'proposal',
                                              'BusinessProposal/contentPage.html', 5, page=page, my=my)


        except ObjectDoesNotExist:

            proposalsPage = func.emptyCompany()
    else:
        result = _proposalDetailContent(request, item_id)
        proposalsPage = result[0]

        description = result[1]
        title = result[2]


    if not request.is_ajax():

        current_section = _("Business Proposal")

        templateParams = {
            'current_section': current_section,
            'proposalsPage': proposalsPage,
            'scripts': scripts,
            'styles': styles,
            'addNew': reverse('proposal:add'),
            'item_id': item_id,
            'description': description,
            'title': title
        }

        return render_to_response("BusinessProposal/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': proposalsPage
        }

        return HttpResponse(json.dumps(serialize))


def _proposalDetailContent(request, item_id):

    lang = settings.LANGUAGE_CODE
    cache_name = "%s_detail_%s" % (lang, item_id)
    description_cache_name = "description_%s" % item_id
    cached = cache.get(cache_name)

    if not cached:

        proposal = get_object_or_404(BusinessProposal, pk=item_id)
        proposalValues = proposal.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SLUG'))
        description = proposalValues.get('DETAIL_TEXT', False)[0] if proposalValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = proposalValues.get('NAME', False)[0] if proposalValues.get('NAME', False) else ""

        photos = Gallery.objects.filter(c2p__parent=item_id)

        additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

        func.addToItemDictinoryWithCountryAndOrganization(proposal.id, proposalValues, withContacts=True)

        template = loader.get_template('BusinessProposal/detailContent.html')

        templateParams = {
            'proposalValues': proposalValues,
            'photos': photos,
            'additionalPages': additionalPages,
            'item_id': item_id
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, (description, title), 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        result = cache.get(description_cache_name)
        description = result[0]
        title = result[1]

    return rendered, description, title


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
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    categories = BpCategories.objects.all()
    categories_id = [categorory.id for categorory in categories]
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
    item = Organization.objects.get(p2c__child_id=item_id)

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
         photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]

    perm_list = item.getItemInstPermList(request.user)

    if 'change_businessproposal' not in perm_list:
        return func.permissionDenied()

    branches = Branch.objects.all()
    branches_ids = [branch.id for branch in branches]
    branches = Item.getItemsAttributesValues(("NAME",), branches_ids)

    categories = BpCategories.objects.all()
    categories_id = [categorory.id for categorory in categories]
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
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_businessproposal' not in perm_list:
        return func.permissionDenied()

    instance = BusinessProposal.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('proposal:main'))


