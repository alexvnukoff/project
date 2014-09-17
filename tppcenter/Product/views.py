from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _, trans_real
from django.utils.timezone import now
from haystack.query import SearchQuerySet
from appl import func
from appl.models import Product, Gallery, AdditionalPages, Company, Category, Organization
from core.models import Item, Dictionary
from core.tasks import addProductAttrubute
from tppcenter.cbv import ItemsList, ItemDetail
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages


class get_products_list(ItemsList):

    #pagination url
    url_paginator = "products:paginator"
    url_my_paginator = "products:my_main_paginator"

    #Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    paginate_by = 12

    current_section = _("Products")
    addUrl = 'products:add'

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = Product

    def get_context_data(self, **kwargs):
        context = super(get_products_list, self).get_context_data(**kwargs)

        context['update_url'] = 'update'

        return context

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/index.html'

    def get_queryset(self):
        sqs = super(get_products_list, self).get_queryset()

        return sqs.exclude(sites=Site.objects.get(name="centerpokupok").pk)

class get_products_b2c_list(ItemsList):

    #pagination url
    url_my_paginator = "products:my_main_b2c_paginator"

    #Lists of required scripts and styles for ajax request
    scripts = []
    styles = []

    paginate_by = 12

    current_section = _("Products B2C")
    addUrl = 'products:addB2C'

    #allowed filter list
    filterList = ['tpp', 'country', 'company', 'branch']

    model = Product

    def get_context_data(self, **kwargs):
        context = super(get_products_b2c_list, self).get_context_data(**kwargs)

        context['update_url'] = 'updateB2C'

        return context

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'Products/index.html'

    def get_queryset(self):
        sqs = super(get_products_b2c_list, self).get_queryset()

        return sqs.filter(sites=Site.objects.get(name="centerpokupok").pk)


class get_product_detail(ItemDetail):

    model = Product
    template_name = 'Products/detailContent.html'

    current_section = _("Products")
    addUrl = 'products:add'

    def get_context_data(self, **kwargs):
        context = super(get_product_detail, self).get_context_data(**kwargs)

        context.update({
            'photos': self._get_gallery(),
            'additionalPages': self._get_additional_pages(),
        })

        return context

@login_required(login_url='/login/')
def productForm(request, action, item_id=None):
    if item_id:
        if not Product.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()


    current_section = _("Products")
    productsPage = ''

    if action == 'delete':
        productsPage = deleteProduct(request, item_id)
    elif action == 'add':
        productsPage = addProducts(request)
    elif action == 'update':
        productsPage = updateProduct(request, item_id)
    elif action == 'update_b2c':
        productsPage = updateProductB2C(request, item_id)
    elif action == 'add_b2c':
        productsPage = addProductsB2C(request)

    if isinstance(productsPage, HttpResponseRedirect) or isinstance(productsPage, HttpResponse):
        return productsPage

    templateParams = {
        'formContent': productsPage,
        'current_section': current_section,
        'item_id': item_id
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))



def addProductsB2C(request):
    current_company = request.session.get('current_company', False)

    categorySite = Site.objects.get(name="centerpokupok").pk

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    try:
        item = Company.objects.get(pk=current_company)
    except ObjectDoesNotExist:
        return func.emptyCompany()


    perm_list = item.getItemInstPermList(request.user)

    if 'add_product' not in perm_list:
         return func.permissionDenied()

    form = None
    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    pages = None
    choosen_category = {}

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

        form = ItemForm('Product', values=values)
        form.clean()

        categories = request.POST.getlist('category[]')

        if not categories:
            categories = []

        choosen_category = Category.objects.filter(pk__in=categories, sites=categorySite)

        if not choosen_category.exists():
            form.errors.update({"CATEGORY": _("You must choose one category at least")})
        else:
            cats = [cat.pk for cat in choosen_category]
            choosen_category = Item.getItemsAttributesValues('NAME', cats)

        if gallery.is_valid() and form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            site = Site.objects.get(name="centerpokupok")

            addProductAttrubute.delay(request.POST, request.FILES, user, site.pk,
                                      current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('products:main'))


    template = loader.get_template('Products/addFormB2C.html')

    templateParams = {
        'form': form,
        'measurement_slots': measurement_slots,
        'currency_slots': currency_slots,
        'pages': pages,
        'choosen_category': choosen_category,
        'categorySite': categorySite
    }

    context = RequestContext(request, templateParams)
    productsPage = template.render(context)

    return productsPage


def addProducts(request):
    current_company = request.session.get('current_company', False)

    categorySite = Site.objects.get(name="tppcenter").pk


    if not request.session.get('current_company', False):
         return func.emptyCompany()

    try:
        item = Company.objects.get(pk=current_company)
    except ObjectDoesNotExist:
        return func.emptyCompany()


    perm_list = item.getItemInstPermList(request.user)

    if 'add_product' not in perm_list:
         return func.permissionDenied()

    form = None
    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    pages = None
    choosen_category = {}

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

        form = ItemForm('Product', values=values)
        form.clean()

        categories = request.POST.getlist('category[]')

        if not categories:
            categories = []

        choosen_category = Category.objects.filter(pk__in=categories, sites=categorySite)

        if not choosen_category.exists():
            form.errors.update({"CATEGORY": _("You must choose one category at least")})
        else:
            cats = [cat.pk for cat in choosen_category]
            choosen_category = Item.getItemsAttributesValues('NAME', cats)

        if gallery.is_valid() and form.is_valid():

            func.notify("item_creating", 'notification', user=request.user)

            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID,
                                      current_company=current_company, lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('products:main'))


    template = loader.get_template('Products/addForm.html')

    templateParams = {
        'form': form,
        'measurement_slots': measurement_slots,
        'currency_slots': currency_slots,
        'pages': pages,
        'categorySite': categorySite,
        'choosen_category': choosen_category
    }

    context = RequestContext(request, templateParams)
    productsPage = template.render(context)

    return productsPage


def updateProduct(request, item_id):

    try:
        item = Company.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        return func.emptyCompany()


    perm_list = item.getItemInstPermList(request.user)

    if 'change_product' not in perm_list:
        return func.permissionDenied()

    categorySite = Site.objects.get(name="tppcenter").pk

    choosen_category = Category.objects.filter(p2c__child=item_id, sites=categorySite)

    categories_ids = [cat.pk for cat in choosen_category]

    categories = Item.getItemsAttributesValues('NAME', categories_ids)



    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    product = Product.objects.get(pk=item_id)


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

    coupon_date = Product.objects.get(pk=item_id).getAttributeValues("COUPON_DISCOUNT", fullAttrVal=True)
    coupon_date = coupon_date[0] if len(coupon_date) > 0 else ""


    form = ItemForm('Product', id=item_id)

    if request.POST:




        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)



        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Product', values=values, id=item_id)
        form.clean()

        categories = request.POST.getlist('category[]')

        if not Category.objects.filter(pk__in=categories, sites=categorySite).exists():
            form.errors.update({"CATEGORY": _("You must choose one category at least")})

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                      lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))


    template = loader.get_template('Products/addForm.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'coupon_date': coupon_date,
        'measurement_slots': measurement_slots,
        'currency_slots': currency_slots,
        'pages': pages,
        'product': product,
        'choosen_category': categories,
        'categorySite': categorySite
    }

    context = RequestContext(request, templateParams)

    productsPage = template.render(context)

    return productsPage


def updateProductB2C(request, item_id):

    try:
        item = Company.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        return func.emptyCompany()


    perm_list = item.getItemInstPermList(request.user)

    if 'change_product' not in perm_list:
        return func.permissionDenied()

    categorySite = Site.objects.get(name="centerpokupok").pk

    choosen_category = Category.objects.filter(p2c__child=item_id)

    categories_ids = [cat.pk for cat in choosen_category]

    categories = Item.getItemsAttributesValues('NAME', categories_ids)



    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()

    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()

    product = Product.objects.get(pk=item_id)


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

    coupon_date = Product.objects.get(pk=item_id).getAttributeValues("COUPON_DISCOUNT", fullAttrVal=True)
    coupon_date = coupon_date[0] if len(coupon_date) > 0 else ""


    form = ItemForm('Product', id=item_id)

    if request.POST:


        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)



        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('Product', values=values, id=item_id)
        form.clean()

        categories = request.POST.getlist('category[]')

        if not Category.objects.filter(pk__in=categories, sites=categorySite).exists():
            form.errors.update({"CATEGORY": _("You must choose one category at least")})

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                      lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))


    template = loader.get_template('Products/addFormB2C.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'coupon_date': coupon_date,
        'measurement_slots': measurement_slots,
        'currency_slots': currency_slots,
        'pages': pages,
        'product': product,
        'choosen_category': categories,
        'categorySite': categorySite
    }

    context = RequestContext(request, templateParams)

    productsPage = template.render(context)

    return productsPage



def deleteProduct(request, item_id):
    item = Organization.objects.get(p2c__child=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_product' not in perm_list:
        return func.permissionDenied()

    instance = Product.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))

def categoryList(request, site):

    parent = request.GET.get('parent', 0)

    try:
        parent = int(parent)
    except:
        parent = 0

    object_list = []
    bread_crumbs = None

    if parent == 0:
        categories = Category.hierarchy.getRootParents(siteID=site)
        catList = [cat.pk for cat in categories]
        object_list = SearchQuerySet().models(Category).filter(django_id__in=catList, sites=site)
    else:
        object_list = SearchQuerySet().models(Category).filter(parent=parent, sites=site)
        bread_crumbs = _get_parents(SearchQuerySet().models(Category).filter(django_id=parent, sites=site))

    new_obj_list = []

    for obj in object_list:
        obj.childs = SearchQuerySet().models(Category).filter(parent=obj.pk, sites=site).count()
        new_obj_list.append(obj)



    templateParams = {
        'object_list': new_obj_list[::-1],
        'bread_crumbs': bread_crumbs
    }

    return render_to_response('Products/categoryList.html', templateParams, context_instance=RequestContext(request))


def _get_parents(parentList):

    if not isinstance(parentList, list):
        obj = parentList[0]
        parentList = [obj]
    else:
        obj = parentList[len(parentList) - 1]

    if obj.parent != 0:
        parentList.append(SearchQuerySet().filter(django_id=obj.parent))
        return _get_parents(parentList)
    else:
        return parentList
