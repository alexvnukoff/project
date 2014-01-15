from django.shortcuts import render
from django.shortcuts import render_to_response
from appl.models import News, Product , Comment
from core.models import Value, Item, Attribute, Dictionary, Relationship
from appl import func
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from tppcenter.forms import ItemForm
from django.template import RequestContext

from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings

def productList(request):
    page = request.GET.get('page', 1)
    result = func.getItemsListWithPagination("News", "Name", "Active_From", "Detail_Text", "Photo", page=page)
    newsList = result[0]
    page = result[1]
    paginator_range = func.getPaginatorRange(page)
    flagList = func.getItemsList("Country", "NAME", "Flag")

    return render_to_response("Product/index.html", locals())


def productDetail(request, item_id):
    if request.POST.get('subCom', False):
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

        page = 1
    else:
       form = ItemForm("Comment")
       page = request.GET.get('page', 1)
    try:
        product = Product.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        raise Http404

    productValues = product.getAttributeValues("NAME",)
    productValues = productValues[int(item_id)]            #TODO Jenya remove [id]
    #flagList = func.getItemsList("Country", "NAME", "Flag")
    comments = Comment.getCommentOfItem(parent_id=item_id)
    comments = comments.order_by('-pk')
    result =  func.setPaginationForItemsWithValues(comments, "DETAIL_TEXT", page_num=3, page=page)
    commentsList = result[0]

    for id ,comment in commentsList.items():
        comment['User'] = comments.get(pk=id).create_user
        comment['Date'] = comments.get(pk=id).create_date
    page = result[1]


    paginator_range = func.getPaginatorRange(page)
    commentsList = OrderedDict(sorted(commentsList.items(), reverse=True))

    dictionaryLabels = {"DETAIL_TEXT": "Comment"}
    form.setlabels(dictionaryLabels)


    return render_to_response("Product/detail.html", locals(), context_instance=RequestContext(request))


