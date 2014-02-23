
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





def addBusinessPRoposal(post, files, user, site_id, addAttr=None, item_id=None, branch=None):

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()


    valPost = ('NAME', 'DETAIL_TEXT', 'DOCUMENT_1-CLEAR', 'DOCUMENT_2-CLEAR', 'DOCUMENT_3-CLEAR')
    valFiles = ('DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3')
    values = {}
    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")





    form = ItemForm('BusinessProposal', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    proposal = form.save(user, site_id)
    if proposal:

        if branch:
            branch = Branch.objects.get(pk=branch)
            rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id)
            Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id).delete()
            Relationship.setRelRelationship(parent=branch, child=proposal, user=user)


        gallery.save(parent=proposal.id, user=user)
        pages.save(parent=proposal.id, user=user)
        func.notify("item_created", 'notification', user=user)


    return True


def addNewCompany(post, files, user, site_id, addAttr=None, item_id=None, branch=None):

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()

    valPost = ('NAME', 'DETAIL_TEXT', 'IMAGE-CLEAR', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX',
               'INN', 'SLOGAN', 'EMAIL', 'KEYWORD', 'DIRECTOR', 'KPP', 'OKPO', 'OKATO', 'OKVED', 'ACCOUNTANT',
               'ACCOUNT_NUMBER', 'BANK_DETAILS')
    valFiles = ('IMAGE',)

    values = {}

    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    form = ItemForm('Company', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    company = form.save(user, site_id)
    if company:

        if branch:
            branch = Branch.objects.get(pk=branch)
            rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id)
            Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id).delete()
            Relationship.setRelRelationship(parent=branch, child=company, user=user)



        pages.save(parent=company.id, user=user)
        func.notify("item_created", 'notification', user=user)


    return True




def addTppAttrubute(post, files, user, site_id, addAttr=None, item_id=None):


    values = {}
    values['NAME'] = post.get('NAME', "")
    values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
    values['YOUTUBE_CODE'] = post.get('YOUTUBE_CODE', "")
    values['IMAGE'] = files.get('IMAGE', "")
    values['IMAGE-CLEAR'] = post.get('IMAGE-CLEAR', " ")
    category = post.get('NEWS_CATEGORY', "")
    category = NewsCategories.objects.get(pk=category) if category else False

    form = ItemForm('TppTV', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    new = form.save(user, site_id)
    if new:


        if category:
            Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=category, child=new, user=user)

        func.notify("item_created", 'notification', user=user)


    return True




def addNewTpp(post, files, user, site_id, addAttr=None, item_id=None):

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()

    valPost = ('NAME', 'DETAIL_TEXT', 'IMAGE-CLEAR', 'FLAG-CLEAR', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX',
               'INN', 'SLOGAN', 'EMAIL', 'KEYWORD', 'DIRECTOR', 'KPP', 'OKPO', 'OKATO', 'OKVED', 'ACCOUNTANT',
               'ACCOUNT_NUMBER', 'BANK_DETAILS')
    valFiles = ('IMAGE', 'FLAG')

    values = {}

    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    form = ItemForm('Tpp', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    tpp = form.save(user, site_id)
    if tpp:

        pages.save(parent=tpp.id, user=user)
        func.notify("item_created", 'notification', user=user)

    return True


#@shared_task
def addNewTender(post, files, user, site_id, addAttr=None, item_id=None):

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()


    valPost = ('NAME', 'COST', 'CURRENCY', 'KEYWORD', 'DETAIL_TEXT', 'DOCUMENT_1-CLEAR', 'DOCUMENT_2-CLEAR',
               'DOCUMENT_3-CLEAR', 'START_EVENT_DATE', 'END_EVENT_DATE')
    valFiles = ('DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3')
    values = {}
    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    form = ItemForm('Tender', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    tender = form.save(user, site_id)
    if tender:


        gallery.save(parent=tender.id, user=user)
        pages.save(parent=tender.id, user=user)
        func.notify("item_created", 'notification', user=user)


    return True
