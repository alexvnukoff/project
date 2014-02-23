from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
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

from core.tasks import addProductAttrubute
from django.conf import settings

def get_product_list(request, page=1, id=None):
    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "Products"

    if id is None:
        productsPage = _productContent(request, page)
    else:
        productsPage = _getDetailContent(request, id)






    return render_to_response("Products/index.html", {'user_name': user_name, 'current_section': current_section,
                                                  'productsPage': productsPage, 'notification': notification},
                              context_instance=RequestContext(request))


def _productContent(request, page=1):
    #TODO Jenya change to get_active_related()
    products = Product.active.get_active().filter(sites__id=settings.SITE_ID).order_by('-pk')


    result = func.setPaginationForItemsWithValues(products, *('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), page_num=12, page=page)

    productsList = result[0]
    products_ids = [id for id in productsList.keys()]
    countries = Country.objects.filter(p2c__child__p2c__child__in=products_ids).values('p2c__child__p2c__child', 'pk')
    countries_id = [country['pk'] for country in countries]
    countriesList = Item.getItemsAttributesValues(("NAME", 'FLAG'), countries_id)
    country_dict = {}
    for country in countries:
        country_dict[country['p2c__child__p2c__child']] = country['pk']

    for id, product in productsList.items():
        toUpdate = {'COUNTRY_NAME': countriesList[country_dict[id]].get('NAME', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_FLAG': countriesList[country_dict[id]].get('FLAG', 0) if country_dict.get(id, 0) else [0],
                    'COUNTRY_ID':  country_dict.get(id, 0)}
        product.update(toUpdate)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)



    url_paginator = "products:paginator"
    template = loader.get_template('Products/contentPage.html')
    context = RequestContext(request, {'productsList': productsList, 'page': page, 'paginator_range': paginator_range,
                                                  'url_paginator': url_paginator})
    return template.render(context)





def _getDetailContent(request, item_id):

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
     return template.render(context)







def addProducts(request):
    form = None
    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()



    if request.POST:
        func.notify("item_creating", 'notification', user=request.user)
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
            addProductAttrubute(request.POST, request.FILES, user, settings.SITE_ID)
            return HttpResponseRedirect(reverse('products:main'))





    return render_to_response('Products/addForm.html', {'form': form, 'measurement_slots': measurement_slots,
                                                        'currency_slots': currency_slots},
                              context_instance=RequestContext(request))



def updateProduct(request, item_id):
    measurement = Dictionary.objects.get(title='MEASUREMENT_UNIT')
    measurement_slots = measurement.getSlotsList()
    currency = Dictionary.objects.get(title='CURRENCY')
    currency_slots = currency.getSlotsList()


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
        func.notify("item_creating", 'notification', user=request.user)

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
            addProductAttrubute(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id)
            return HttpResponseRedirect(reverse('products:main'))







    return render_to_response('Products/addForm.html', {'gallery': gallery, 'photos': photos, 'form': form, 'coupon_date':
                                                    coupon_date, 'measurement_slots': measurement_slots,
                                                    'currency_slots': currency_slots, 'pages': pages},
                              context_instance=RequestContext(request))



