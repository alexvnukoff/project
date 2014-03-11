from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from haystack.query import SQ, SearchQuerySet
import json
from core.tasks import addProductAttrubute
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def get_product_list(request, page=1, item_id=None, my=None, slug=None):

    filterAdv = []

    if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
         slug = Value.objects.get(item=item_id, attr__title='SLUG').title
         return HttpResponseRedirect(reverse('products:detail',  args=[slug]))

    cabinetValues = func.getB2BcabinetValues(request)
    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    if item_id is None:
        try:
            productsPage, filterAdv = _productContent(request, page, my)
        except ObjectDoesNotExist:
            return render_to_response("permissionDen.html")
    else:
        productsPage, filterAdv = _getDetailContent(request, item_id)

    styles = []
    scripts = []

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    tops = func.getTops(request, {Product: 5, InnovationProject: 5, Company: 5, BusinessProposal: 5}, filter=filterAdv)


    if not request.is_ajax() or item_id:
        user = request.user
        if user.is_authenticated():
            notification = Notification.objects.filter(user=request.user, read=False).count()
            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = _("Products")

        templateParams = {
                'user_name': user_name,
                'current_section': current_section,
                'productsPage': productsPage,
                'notification': notification,
                'current_company': current_company,
                'scripts': scripts,
                'styles': styles,
                'search': request.GET.get('q', ''),
                'addNew': reverse('products:add'),
                'cabinetValues': cabinetValues,
                'bannerRight': bRight,
                'bannerLeft': bLeft,
                'tops': tops
        }

        return render_to_response("Products/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': productsPage,
            'current_company': current_company,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return HttpResponse(json.dumps(serialize))


def _productContent(request, page=1, my=None):
    #TODO: Jenya change to get_active_related()
    #products = Product.active.get_active().order_by('-pk')

    filterAdv = []

    if not my:
        filters, searchFilter, filterAdv = func.filterLive(request)

        sqs = SearchQuerySet().models(Product)

        if len(searchFilter) > 0:
            sqs = sqs.filter(**searchFilter)

        q = request.GET.get('q', '')

        if q != '':
            sqs = sqs.filter(SQ(title=q) | SQ(text=q))

        sortFields = {
            'date': 'id',
            'name': 'title'
        }

        order = []

        sortField1 = request.GET.get('sortField1', 'date')
        sortField2 = request.GET.get('sortField2', None)
        order1 = request.GET.get('order1', 'desc')
        order2 = request.GET.get('order2', None)

        if sortField1 and sortField1 in sortFields:
            if order1 == 'desc':
                order.append('-' + sortFields[sortField1])
            else:
                order.append(sortFields[sortField1])
        else:
            order.append('-id')

        if sortField2 and sortField2 in sortFields:
            if order2 == 'desc':
                order.append('-' + sortFields[sortField2])
            else:
                order.append(sortFields[sortField2])

        products = sqs.order_by(*order)

        params = {
        'filters': filters,
        'sortField1': sortField1,
        'sortField2': sortField2,
        'order1': order1,
        'order2': order2
        }
        url_paginator = "products:paginator"
    else:
         current_organization = request.session.get('current_company', False)

         if current_organization:
             products = SearchQuerySet().models(Product).filter(sites=settings.SITE_ID).\
                 filter(SQ(tpp=current_organization)|SQ(company=current_organization))

             url_paginator = "products:my_main_paginator"
             params = {}
         else:
             raise ObjectDoesNotExist('you need check company')




    result = func.setPaginationForSearchWithValues(products, *('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), page_num=12, page=page)
    #result = func.setPaginationForItemsWithValues(products, *('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), page_num=12, page=page)

    productsList = result[0]
    products_ids = [id for id in productsList.keys()]
    countries = Country.objects.filter(p2c__child__p2c__child__in=products_ids, p2c__type='dependence',
                                       p2c__child__p2c__type='dependence').values('p2c__child__p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}

    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, product in productsList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', [0]) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', [0]) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        product.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)




    template = loader.get_template('Products/contentPage.html')

    templateParams = {
        'productsList': productsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,

    }

    templateParams.update(params)

    context = RequestContext(request, templateParams)
    return template.render(context), filterAdv





def _getDetailContent(request, item_id):

     filterAdv = func.getDeatailAdv(item_id)

     product = get_object_or_404(Product, pk=item_id)
     productValues = product.getAttributeValues(*('NAME', 'COST', 'CURRENCY', 'IMAGE',
                                                'DETAIL_TEXT', 'COUPON_DISCOUNT', 'DISCOUNT', 'MEASUREMENT_UNIT',
                                                'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SKU'))

     photos = Gallery.objects.filter(c2p__parent=item_id)

     additionalPages = AdditionalPages.objects.filter(c2p__parent=item_id)

     country = Country.objects.get(p2c__child__p2c__child=item_id)




     company = Company.objects.get(p2c__child=item_id)
     companyValues = company.getAttributeValues("NAME", 'ADDRESS', 'FAX', 'TELEPHONE_NUMBER', 'SITE_NAME')
     companyValues.update({'COMPANY_ID': company.id})


     countriesList = country.getAttributeValues("NAME", 'FLAG')
     toUpdate = {'COUNTRY_NAME': countriesList.get('NAME', 0),
                 'COUNTRY_FLAG': countriesList.get('FLAG', 0),
                 'COUNTRY_ID':  country.id}
     companyValues.update(toUpdate)





     template = loader.get_template('Products/detailContent.html')

     context = RequestContext(request, {'productValues': productValues, 'photos': photos,
                                        'additionalPages': additionalPages, 'companyValues': companyValues})

     return template.render(context), filterAdv



@login_required(login_url='/login/')
def productForm(request, action, item_id=None):
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    user = request.user

    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()

        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name

    else:

        user_name = None
        notification = None

    current_section = _("Products")

    if action == 'add':
        productsPage = addProducts(request)
    else:
        productsPage = updateProduct(request, item_id)

    if isinstance(productsPage, HttpResponseRedirect) or isinstance(productsPage, HttpResponse):
        return productsPage

    return render_to_response('Products/index.html', {'productsPage': productsPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))


def addProducts(request):
    current_company = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return render_to_response("permissionDen.html")

    try:
        item = Company.objects.get(pk=current_company)
    except ObjectDoesNotExist:
        return render_to_response("permissionDen.html")


    perm_list = item.getItemInstPermList(request.user)



    if 'add_product' not in perm_list:
         return render_to_response("permissionDenied.html")



    form = None
    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    categories_id = [cat['ID'] for cat in hierarchyStructure]
    categories = Item.getItemsAttributesValues(("NAME",), categories_id)
    categotySelect = func.setStructureForHiearhy(hierarchyStructure, categories)



    if request.POST:

        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")



        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['COST'] = request.POST.get('COST', "")
        values['CURRENCY'] = request.POST.get('CURRENCY', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['COUPON_DISCOUNT'] = request.POST.get('COUPON_DISCOUNT', "")
        values['DISCOUNT'] = request.POST.get('DISCOUNT', "")
        values['MEASUREMENT_UNIT'] = request.POST.get('MEASUREMENT_UNIT', "")
        values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
        values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
        values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")
        values['SMALL_IMAGE'] = request.FILES.get('SMALL_IMAGE', "")
        values['SKU'] = request.POST.get('SKU', "")




        form = ItemForm('Product', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid() and pages.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('products:main'))


    template = loader.get_template('Products/addForm.html')
    context = RequestContext(request, {'form': form, 'measurement_slots': measurement_slots,
                                                        'currency_slots': currency_slots,
                                                        'categotySelect': categotySelect})
    productsPage = template.render(context)


    return productsPage



def updateProduct(request, item_id):
    try:
        item = Company.objects.get(p2c__child_id=item_id)
    except ObjectDoesNotExist:
        return render_to_response("permissionDen.html")


    perm_list = item.getItemInstPermList(request.user)
    if 'change_exhibition' not in perm_list:
        return render_to_response("permissionDenied.html")
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

        Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
        pages = Page(request.POST, request.FILES, prefix="pages")

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['COST'] = request.POST.get('COST', "")
        values['CURRENCY'] = request.POST.get('CURRENCY', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['COUPON_DISCOUNT'] = request.POST.get('COUPON_DISCOUNT', "")
        values['DISCOUNT'] = request.POST.get('DISCOUNT', "")
        values['MEASUREMENT_UNIT'] = request.POST.get('MEASUREMENT_UNIT', "")
        values['DOCUMENT_1'] = request.FILES.get('DOCUMENT_1', "")
        values['DOCUMENT_2'] = request.FILES.get('DOCUMENT_2', "")
        values['DOCUMENT_3'] = request.FILES.get('DOCUMENT_3', "")
        values['SMALL_IMAGE'] = request.FILES.get('SMALL_IMAGE', "")
        values['SKU'] = request.POST.get('SKU', "")

        form = ItemForm('Product', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addProductAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('products:main'))




    template = loader.get_template('Products/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form, 'coupon_date':
                                                    coupon_date, 'measurement_slots': measurement_slots,
                                                    'currency_slots': currency_slots, 'pages': pages,
                                                    'product': product, 'choosen_category': choosen_category,
                                                     'categotySelect': categotySelect})
    productsPage = template.render(context)


    return productsPage



