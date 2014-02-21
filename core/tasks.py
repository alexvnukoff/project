
from appl.models import *

from django.forms.models import modelformset_factory

from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages

from celery import shared_task, task

from appl import func


@shared_task
def addNewsAttrubute(post, files, user, site_id, addAttr=None, item_id=None):
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    values = {}
    values['NAME'] = post.get('NAME', "")
    values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
    values['YOUTUBE_CODE'] = post.get('YOUTUBE_CODE', "")
    values['IMAGE'] = files.get('IMAGE', "")
    values['IMAGE-CLEAR'] = post.get('IMAGE-CLEAR', " ")
    category = post.get('NEWS_CATEGORY', "")
    category = NewsCategories.objects.get(pk=category) if category else False

    form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    new = form.save(user, site_id)
    if new:
        gallery.save(parent=new.id, user=user)

        if category:
            Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=category, child=new, user=user)

        func.notify("item_created", 'notification', user=user)


    return True


#@shared_task
def addProductAttrubute(post, files, user, site_id, addAttr=None, item_id=None):

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()


    valPost = ('NAME', 'COST', 'CURRENCY', 'ANONS', 'KEYWORD', 'DETAIL_TEXT', 'COUPON_DISCOUNT', 'DISCOUNT',
               'MEASUREMENT_UNIT', 'ANONS', 'SKU', 'IMAGE-CLEAR', 'DOCUMENT_1-CLEAR', 'DOCUMENT_2-CLEAR',
               'DOCUMENT_3-CLEAR', 'SMALL_IMAGE-CLEAR')
    valFiles = ('IMAGE', 'DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3', 'SMALL_IMAGE')
    values = {}
    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")


    if post.get('COUPON_DISCOUNT-END', None):
       dates = {'COUPON_DISCOUNT': [post.get('COUPON_DISCOUNT-START', now()), post.get('COUPON_DISCOUNT-END', None)]}
    else:
        dates = None



    form = ItemForm('Product', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    product = form.save(user, site_id, dates=dates)
    if product:


        gallery.save(parent=product.id, user=user)
        pages.save(parent=product.id, user=user)
        func.notify("item_created", 'notification', user=user)


    return True
