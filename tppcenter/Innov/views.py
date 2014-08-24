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
from haystack.query import SearchQuerySet

from appl import func
from appl.models import InnovationProject, Branch, AdditionalPages, Cabinet, Gallery, Organization
from core.tasks import addNewProject
from core.models import Item, Dictionary
from tppcenter.cbv import ItemsList, ItemDetail
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class get_innov_list(ItemsList):

    #pagination url
    url_paginator = "innov:paginator"
    url_my_paginator = "innov:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = InnovationProject

    def _get_branches_data_for_objects(self, object_list):
        new_object_list = []

        for obj in object_list:
            obj.__setattr__('branch', SearchQuerySet().models(Branch).filter(django_id__in=obj.branch))
            new_object_list.append(obj)

        return new_object_list

    def _get_cabinet_data_for_objects(self, object_list):
        new_object_list = []

        for obj in object_list:
            if obj.cabinet:
                obj.__setattr__('cabinet', SearchQuerySet().models(Cabinet).filter(django_id=obj.cabinet))
            new_object_list.append(obj)

        return new_object_list

    def get_context_data(self, **kwargs):
        context = super(get_innov_list, self).get_context_data(**kwargs)

        context['object_list'] = self._get_branches_data_for_objects(context['object_list'])
        context['object_list'] = self._get_cabinet_data_for_objects(context['object_list'])

        return context


    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Innov/index.html'


class get_innov_detail(ItemDetail):

    model = InnovationProject
    template_name = 'Innov/detailContent.html'

    current_section = _("Innovation Project")
    addUrl = 'innov:add'

    def _get_branches_data_for_object(self):

        return SearchQuerySet().filter(django_id__in=self.object.branch)


    def _get_cabinet_data_for_object(self):
        return SearchQuerySet().filter(django_id=self.object.cabinet)

    def get_context_data(self, **kwargs):
        context = super(get_innov_detail, self).get_context_data(**kwargs)
        context[self.context_object_name].__setattr__('branch', self._get_branches_data_for_object())
        context[self.context_object_name].__setattr__('cabinet', self._get_cabinet_data_for_object())

        context.update({
            'photos': self._get_gallery(),
            'additionalPages': self._get_additional_pages(),
        })

        return context


@login_required(login_url='/login/')
def innovForm(request, action, item_id=None):

    if item_id:
       if not InnovationProject.active.get_active().filter(django_id=item_id).exists():
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
            addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, branch=branch,
                                current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('innov:main'))


    template = loader.get_template('Innov/addForm.html')
    context = RequestContext(request, {'form': form, 'branches': branches, 'currency_slots': currency_slots, 'pages': pages})
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
            addNewProject.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                branch=branch, lang_code=trans_real.get_language())

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

