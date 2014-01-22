from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import News, Product, Comment, Category, Company, Country
from core.models import Value, Item, Attribute, Dictionary, Relationship
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from tppcenter.forms import ItemForm
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.db.models import Q
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings

def productList(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Name", "Active_From", "Detail_Text", "Photo", page=page)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    flagList = func.getItemsList("Country", "NAME", "FLAG")

    return render_to_response("Product/index.html", locals())


def productDetail(request, item_id):
    if request.POST.get('subCom', False):
        form = addComment(request, item_id)
        if isinstance(form, HttpResponseRedirect):
            return form

    else:
        form = ItemForm("Comment")
    page = request.GET.get('page', 1)


    product = get_object_or_404(Product, pk=item_id)
    productValues = product.getAttributeValues("NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY')

    category = Category.objects.filter(p2c__child_id=item_id).values_list("pk")
    sameProducts = Product.objects.filter(c2p__parent_id__in=category).exclude(pk=item_id)
    product_id = [prod.id for prod in sameProducts]
    sameProducts = Item.getItemsAttributesValues(("NAME", "IMAGE", "CURRENCY", "COST"), product_id)




    flagList = func.getItemsList("Country", "NAME", "FLAG")

    result = _getComment(item_id, page)
    commentsList = result[0]
    paginator_range = result[1]
    page = result[2]

    dictionaryLabels = {"DETAIL_TEXT": "Comment"}
    form.setlabels(dictionaryLabels)



    return render_to_response("Product/detail.html", locals(), context_instance=RequestContext(request))


def addComment(request, item_id):

        form = ItemForm("Comment", values=request.POST)
        form.clean()
        spam = Comment.spamCheck(user=request.user, parent_id=item_id)
        if(spam):
            form._errors["DETAIL_TEXT"] = _("You can send one comment per minute")

        if form.is_valid():
            i = request.user
            comment = form.save(request.user)
            parent = Product.objects.get(pk=item_id)
            Relationship.setRelRelationship(parent, comment, request.user)
            return HttpResponseRedirect(reverse("products:detail", args=[item_id]))

        else:
            return form



def getCategoryProduct(request, category_id):

    page = request.GET.get("page", 1)

    products = Product.objects.filter(c2p__parent_id=category_id, c2p__type='rel', sites=settings.SITE_ID).order_by("-pk")
    result = func.setPaginationForItemsWithValues(products, "NAME", 'DETAIL_TEXT', 'IMAGE', 'COST', 'CURRENCY',
                                         page_num=12, page=1)
    products_list = result[0]
    products_ids = [key for key, value in products_list.items()]
    companies = Company.objects.filter(p2c__child_id__in=products_ids)
    items = Item.objects.filter(p2c__child_id__in=companies, p2c__type="rel", pk__in=Country.objects.all(),
                                 p2c__child__p2c__child__in=products_ids).values("country", "p2c__child_id",
                                                                                 'p2c__child__p2c__child', 'pk')
    items_id =[]
    for item in items:
        items_id.append(item['pk'])
        items_id.append(item['p2c__child_id'])

    items_id = set(items_id)
    itemsWithAttribute = Item.getItemsAttributesValues(("NAME", "IMAGE"), items_id)
    companyList = {}
    for item in items:
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_NAME': itemsWithAttribute[item['p2c__child_id']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_IMAGE': itemsWithAttribute[item['p2c__child_id']]['IMAGE']})
        products_list[item['p2c__child__p2c__child']].update({'COMPANY_ID': item['p2c__child_id']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_NAME': itemsWithAttribute[item['pk']]['NAME']})
        products_list[item['p2c__child__p2c__child']].update({'COUNTRY_ID': item['pk']})
        if item["p2c__child_id"] not in companyList:
            companyList[item["p2c__child_id"]] = {}
            companyList[item["p2c__child_id"]].update({"COMPANY_NAME": itemsWithAttribute[item['p2c__child_id']]['NAME']})
            companyList[item["p2c__child_id"]].update({"COMPANY_IMAGE": itemsWithAttribute[item['p2c__child_id']]['IMAGE']})
            companyList[item["p2c__child_id"]].update({"COUNTRY_NAME": itemsWithAttribute[item['pk']]['NAME']})
            companyList[item['p2c__child_id']].update({'COUNTRY_ID': item['pk']})



    page = result[1]
    paginator_range = func.getPaginatorRange(page)




    return render_to_response("Product/index.html", {'products_list': products_list,'companyList': companyList,
                                                      'page': page, 'paginator_range': paginator_range})











def _getComment(parent_id, page):
    comments = Comment.getCommentOfItem(parent_id=parent_id)
    comments = comments.order_by('-pk')
    result = func.setPaginationForItemsWithValues(comments, "DETAIL_TEXT", page_num=3, page=page)
    commentsList = result[0]

    for id ,comment in commentsList.items():
        comment['User'] = comments.get(pk=id).create_user
        comment['Date'] = comments.get(pk=id).create_date
    page = result[1]


    paginator_range = func.getPaginatorRange(page)
    commentsList = OrderedDict(sorted(commentsList.items(), reverse=True))

    return commentsList, paginator_range , page




