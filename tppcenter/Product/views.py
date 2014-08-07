from appl import func
from appl.models import Product, Gallery, AdditionalPages, Company, Country, Category, Organization
from core.models import Item, Dictionary
from core.tasks import addProductAttrubute
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _, trans_real
from django.utils.timezone import now
from tppcenter.forms import ItemForm, BasePhotoGallery, BasePages
import json


def get_product_list(request, page=1, item_id=None, my=None, slug=None):


   # if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('products:detail',  args=[slug]))
    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()

    description = ''
    title = ''

    if item_id is None:
        try:
            attr  = ('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG')
            productsPage = func.setContent(request, Product, attr, 'products', 'Products/contentPage.html', 12,
                                           page=page, my=my)

        except ObjectDoesNotExist:
            productsPage = func.emptyCompany()
    else:
        result = _getDetailContent(request, item_id)
        productsPage = result[0]
        description = result[1]
        title = result[2]
    styles = []
    scripts = []


    if not request.is_ajax() or item_id:
        current_section = _("Products")

        templateParams = {
            'current_section': current_section,
            'productsPage': productsPage,
            'scripts': scripts,
            'styles': styles,
            'addNew': reverse('products:add'),
            'item_id': item_id,
            'description': description,
            'title': title
        }

        return render_to_response("Products/index.html", templateParams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': productsPage,
        }

        return HttpResponse(json.dumps(serialize))


def _getDetailContent(request, item_id):

    lang = settings.LANGUAGE_CODE
    cache_name = "%s_detail_%s" % (lang, item_id)
    description_cache_name = "description_%s" % item_id
    query = request.GET.urlencode()
    cached = cache.get(cache_name)
    if not cached:

        product = get_object_or_404(Product, pk=item_id)

        attr = (
            'NAME', 'COST', 'CURRENCY', 'IMAGE', 'DETAIL_TEXT',
            'COUPON_DISCOUNT', 'DISCOUNT', 'MEASUREMENT_UNIT',
            'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SKU'
        )

        productValues = product.getAttributeValues(*attr)

        description = productValues.get('DETAIL_TEXT', False)[0] if productValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)
        title = productValues.get('NAME', False)[0] if productValues.get('NAME', False) else ""

        photos = Gallery.objects.filter(c2p__parent=item_id)

        additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

        country = Country.objects.get(p2c__child__p2c__child=item_id, p2c__type="dependence", p2c__child__p2c__type="dependence")

        company = Company.objects.get(p2c__child=item_id)
        companyValues = company.getAttributeValues("NAME", 'ADDRESS', 'FAX', 'TELEPHONE_NUMBER', 'SITE_NAME', 'SLUG')
        companyValues.update({'COMPANY_ID': company.id})


        countriesList = country.getAttributeValues("NAME", 'FLAG', 'COUNTRY_FLAG')

        toUpdate = {
            'COUNTRY_NAME': countriesList.get('NAME', 0),
            'COUNTRY_FLAG': countriesList.get('FLAG', 0),
            'FLAG_CLASS': countriesList.get('COUNTRY_FLAG', 0),
            'COUNTRY_ID':  country.id
        }

        companyValues.update(toUpdate)

        template = loader.get_template('Products/detailContent.html')

        templateParams = {
            'productValues': productValues,
            'photos': photos,
            'additionalPages': additionalPages,
            'companyValues': companyValues,
            'item_id': item_id
        }

        context = RequestContext(request, templateParams)
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, (description, title), 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        result = cache.get(description_cache_name)
        description = result[0] if isinstance(result, list) else ""
        title = result[1] if isinstance(result, list) else ""


    return rendered, description, title




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

    if isinstance(productsPage, HttpResponseRedirect) or isinstance(productsPage, HttpResponse):
        return productsPage

    templateParams = {
        'formContent': productsPage,
        'current_section': current_section,
        'item_id': item_id
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addProducts(request):
    current_company = request.session.get('current_company', False)

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

    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)

    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)

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

        form = ItemForm('Product', values=values)
        form.clean()

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
        'categotySelect': categotySelect,
        'pages': pages
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

    try:
        choosen_category = Category.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''

    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)

    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)

    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)


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

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                      lang_code=trans_real.get_language())

            return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))


    template = loader.get_template('Products/addForm.html')

    templateParams =  {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'coupon_date': coupon_date,
        'measurement_slots': measurement_slots,
        'currency_slots': currency_slots,
        'pages': pages,
        'product': product,
        'choosen_category': choosen_category,
        'categotySelect': categotySelect,
        'b2c_product':  Item.objects.get(pk=item_id).sites.filter(name='centerpokupok').exists()
    }

    context = RequestContext(request, templateParams)

    productsPage = template.render(context)

    return productsPage



def deleteProduct(request, item_id):
    item = Organization.objects.get(p2c__child_id=item_id)

    perm_list = item.getItemInstPermList(request.user)

    if 'delete_product' not in perm_list:
        return func.permissionDenied()

    instance = Product.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()




    return HttpResponseRedirect(request.GET.get('next'), reverse('products:main'))