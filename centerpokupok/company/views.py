__author__ = 'user'
from core.models import Item
from appl.models import Company, Category, Product
from django.shortcuts import render_to_response
from appl import func
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

def storeMain(request, company, category=None):

    try:
        companyObj = Company.objects.get(pk=company)
    except ObjectDoesNotExist:
        pass

    #----NEW PRODUCT LIST -----#
    products = Product.getNew().filter(sites=settings.SITE_ID, c2p__parent_id=company)[:4]
    newProducrList = Product.getCategoryOfPRoducts(products, ("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT',
                                                              'DISCOUNT'))

    #----NEW PRODUCT LIST -----#
    products = Product.getNew().filter(sites=settings.SITE_ID, c2p__parent_id=company)[4:8]
    topPoductList = Product.getCategoryOfPRoducts(products, ("NAME", "COST", "CURRENCY", "IMAGE", 'COUPON_DISCOUNT',
                                                              'DISCOUNT'))

    #-------------- Store Categories ---------------#
    storeCategories = companyObj.getStoreCategories()
    hierarchyStructure = Category.hierarchy.getTree(siteID=settings.SITE_ID)
    root_cats = [cat['ID'] for cat in hierarchyStructure if cat['LEVEL'] == 1]
    categories = Item.getItemsAttributesValues(("NAME",), root_cats)

    storeCategories = func._categoryStructure(hierarchyStructure, storeCategories, categories)

    #------ 3 Coupons ----------#
    couponsObj = Product.getCoupons().order_by('item2value__end_date')[:3]
    coupons_ids = [cat.pk for cat in couponsObj]
    coupons = Product.getItemsAttributesValues(("NAME", "COUPON_DISCOUNT", "CURRENCY", "COST", "IMAGE"), coupons_ids,
                                               fullAttrVal=True)
    coupons = func._setCouponsStructure(coupons)

    #----------- Products with discount -------------#
    productsSale = Product.getProdWithDiscount()
    productsSale = func.sortQuerySetByAttr(productsSale, "DISCOUNT", "DESC", "int")[:15]
    productsSale_ids = [prod.pk for prod in productsSale]
    productsSale = Product.getItemsAttributesValues(("NAME", "DISCOUNT", "IMAGE", "COST"), productsSale_ids)
    productsSale = func._setProductStructure(productsSale)

    #------------------- Company Details --------------------#
    attr = companyObj.getAttributeValues('NAME', 'IMAGE')
    name = attr['NAME'][0]
    picture = attr['IMAGE'][0]



    return render_to_response("Company/index.html", {'companyID': company, 'name': name, 'picture': picture,
                                                     'storeCategories': storeCategories, 'coupons': coupons,
                                                     'productsSale': productsSale, 'newProducrList': newProducrList,
                                                     'topPoductList': topPoductList})