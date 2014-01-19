__author__ = 'user'
from django.shortcuts import render_to_response
from appl import func
from appl.models import Product

def couponsList(request):
    page = request.GET.get('page', 1)
    couponsObj = Product.getCoupons().order_by('item2value__end_date')

    attr = ("NAME", "DISCOUNT", "CURRENCY", "COST", "IMAGE")
    result = func.setPaginationForItemsWithValues(couponsObj, page=page, page_num=17, fullAttrVal=True, *attr)
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    coupons = func._setCouponsStructure(result[0])

    return render_to_response("Coupons/index.html", locals())

def couponsDetail(request):
    pass