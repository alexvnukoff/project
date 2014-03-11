
from appl.models import *
from django.utils.translation import trans_real
from django.forms.models import modelformset_factory

from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages

from celery import shared_task, task
import json
from appl import func


@shared_task
def addNewsAttrubute(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    values = {}
    values['NAME'] = post.get('NAME', "")
    values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
    values['YOUTUBE_CODE'] = post.get('YOUTUBE_CODE', "")
    values['IMAGE'] = files.get('IMAGE', "")
    values['IMAGE-CLEAR'] = post.get('IMAGE-CLEAR', "")
    category = post.get('NEWS_CATEGORY', "")
    category = NewsCategories.objects.get(pk=category) if category else False
    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False
    date = post.get('CREATE_DATE', False)



    form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    new = form.save(user, site_id)
    if new:
        if date:
            try:
                date = datetime.datetime.strptime(date, "%m/%d/%Y")
                new.create_date = date
                new.save()
            except Exception as e:
                pass
        gallery.save(parent=new.id, user=user)

        if category:
            Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=category, child=new, user=user)

        if country:
            Relationship.objects.filter(parent__in=Country.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=country, child=new, user=user)

        if current_company:
            Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=new, type='dependence', user=user)

        new.reindexItem()


        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True


@shared_task
def addProductAttrubute(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
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

    start_date = post.get('START_DATE', None)
    end_date = post.get('END_DATE', None)
    category = post.get('CATEGORY', None)

    if post.get('COUPON_DISCOUNT-END', None):
       date = datetime.datetime.strptime(post.get('COUPON_DISCOUNT-END', None), "%m/%d/%Y")
       dates = {'COUPON_DISCOUNT': [post.get('COUPON_DISCOUNT-START', now()), date]}
    else:
        dates = None



    form = ItemForm('Product', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    product = form.save(user, site_id, dates=dates)
    if product:
        if end_date:
            product.start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y")
            product.end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y")
            product.save()

        if category:
            category = Category.objects.get(pk=category)
            Relationship.objects.filter(parent__in=Category.objects.all(), child=product.id).delete()
            Relationship.setRelRelationship(parent=category, child=product, user=user)

        if current_company:
            parent = Organization.objects.get(pk=int(current_company))
            Relationship.setRelRelationship(parent=parent, child=product, type='dependence', user=user)



        gallery.save(parent=product.id, user=user)
        pages.save(parent=product.id, user=user)
        product.reindexItem()
        func.notify("item_created", 'notification', user=user)


    trans_real.deactivate()
    return True




@shared_task
def addBusinessPRoposal(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()


    valPost = ('NAME', 'DETAIL_TEXT', 'DOCUMENT_1-CLEAR', 'DOCUMENT_2-CLEAR', 'DOCUMENT_3-CLEAR', 'KEYWORD')
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

        if current_company:
            Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=proposal, type='dependence', user=user)


        gallery.save(parent=proposal.id, user=user)
        pages.save(parent=proposal.id, user=user)
        proposal.reindexItem()
        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True

@shared_task
def addNewCompany(post, files, user, site_id, addAttr=None, item_id=None, branch=None, lang_code=None):
    trans_real.activate(lang_code)
    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()

    valPost = ('NAME', 'DETAIL_TEXT', 'IMAGE-CLEAR', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX',
               'INN', 'SLOGAN', 'EMAIL', 'KEYWORD', 'DIRECTOR', 'KPP', 'OKPO', 'OKATO', 'OKVED', 'ACCOUNTANT',
               'ACCOUNT_NUMBER', 'BANK_DETAILS', 'ANONS')
    valFiles = ('IMAGE',)

    values = {}

    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    if post.get('Lat', ''):
        values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')



    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False

    tpp = post.get('TPP', False)
    tpp = Tpp.objects.get(pk=tpp) if tpp else False

    form = ItemForm('Company', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    company = form.save(user, site_id)
    if company:



        if branch:
            branch = Branch.objects.get(pk=branch)
            rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id)
            Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id).delete()
            Relationship.setRelRelationship(parent=branch, child=company, user=user)


        if country:
            Relationship.objects.filter(parent__in=Country.objects.all(), child=company.id).delete()
            Relationship.setRelRelationship(parent=country, child=company, user=user, type='dependence')

        if tpp:
            Relationship.objects.filter(parent__in=Tpp.objects.all(), child=company.id).delete()
            Relationship.setRelRelationship(parent=tpp, child=company, user=user)
        else:
            time = now() + datetime.timedelta(days=60)
            company.end_date = time
            company.save()

        g = Group.objects.get(name=company.community)
        g.user_set.add(user)
        company.reindexItem()



        pages.save(parent=company.id, user=user)
        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True



@shared_task
def addTppAttrubute(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
    trans_real.activate(lang_code)

    values = {}
    values['NAME'] = post.get('NAME', "")
    values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
    values['YOUTUBE_CODE'] = post.get('YOUTUBE_CODE', "")
    values['IMAGE'] = files.get('IMAGE', "")
    values['IMAGE-CLEAR'] = post.get('IMAGE-CLEAR', " ")
    category = post.get('NEWS_CATEGORY', "")
    category = NewsCategories.objects.get(pk=category) if category else False
    date = post.get('CREATE_DATE', False)
    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False


    form = ItemForm('TppTV', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    new = form.save(user, site_id)
    if new:
        if date:
            try:
                date = datetime.datetime.strptime(date, "%m/%d/%Y")
                new.create_date = date
                new.save()
            except Exception as e:
                pass


        if category:
            Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=category, child=new, user=user)

        if country:
            Relationship.objects.filter(parent__in=Country.objects.all(), child=new.id).delete()
            Relationship.setRelRelationship(parent=country, child=new, user=user)

        new.reindexItem()

        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True



@shared_task
def addNewTpp(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
    trans_real.activate(lang_code)
    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()

    valPost = ('NAME', 'DETAIL_TEXT', 'IMAGE-CLEAR', 'FLAG-CLEAR', 'ADDRESS', 'SITE_NAME', 'TELEPHONE_NUMBER', 'FAX',
               'INN', 'SLOGAN', 'EMAIL', 'KEYWORD', 'DIRECTOR', 'KPP', 'OKPO', 'OKATO', 'OKVED', 'ACCOUNTANT',
               'ACCOUNT_NUMBER', 'BANK_DETAILS', 'ANONS')
    valFiles = ('IMAGE', 'FLAG')

    values = {}

    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    if post.get('Lat', ''):
        values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')

    start_date = post.get('START_DATE', None)
    end_date = post.get('END_DATE', None)

    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False

    form = ItemForm('Tpp', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    tpp = form.save(user, site_id)
    if tpp:
        if end_date:
            tpp.start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y")
            tpp.end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y")
            tpp.save()





        if country:
            Relationship.objects.filter(parent__in=Country.objects.all(), child=tpp.id).delete()
            Relationship.setRelRelationship(parent=country, child=tpp, user=user, type='dependence')

        tpp.reindexItem()

        pages.save(parent=tpp.id, user=user)
        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True


@shared_task
def addNewTender(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
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
        if current_company:
            Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=tender, type='dependence', user=user)



        tender.reindexItem()



        gallery.save(parent=tender.id, user=user)
        pages.save(parent=tender.id, user=user)
        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True



@shared_task
def addNewExhibition(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()


    valPost = ('NAME', 'CITY', 'KEYWORD', 'ROUTE_DESCRIPTION', 'START_EVENT_DATE', 'END_EVENT_DATE', 'DOCUMENT_1-CLEAR',
               'DOCUMENT_2-CLEAR', 'DOCUMENT_3-CLEAR', )
    valFiles = ('DOCUMENT_1', 'DOCUMENT_2', 'DOCUMENT_3')
    values = {}
    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    if post.get('Lat', ''):
        values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')





    form = ItemForm('Exhibition', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    proposal = form.save(user, site_id)
    if proposal:

        if branch:
            branch = Branch.objects.get(pk=branch)
            rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id)
            Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id).delete()
            Relationship.setRelRelationship(parent=branch, child=proposal, user=user)


        if current_company:
            Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=proposal, type='dependence', user=user)



        proposal.reindexItem()




        gallery.save(parent=proposal.id, user=user)
        pages.save(parent=proposal.id, user=user)
        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True



@shared_task
def addNewProject(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(post, files)

    Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
    pages = Page(post, files, prefix="pages")
    pages.clean()

    valPost = ('NAME', 'PRODUCT_NAME','COST', 'CURRENCY', 'TARGET_AUDIENCE', 'RELEASE_DATE', 'DOCUMENT_1-CLEAR',
                'SITE_NAME', 'KEYWORD', 'DETAIL_TEXT', 'BUSINESS_PLAN')
    valFiles = ('DOCUMENT_1', )
    values = {}
    for val in valPost:
        values[val] = post.get(val, "")
    for val in valFiles:
        values[val] = files.get(val, "")

    form = ItemForm('InnovationProject', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    project = form.save(user, site_id)

    if project:
        if branch:
            branch = Branch.objects.get(pk=branch)
            rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=project.id)
            Relationship.objects.filter(parent__in=Branch.objects.all(), child=project.id).delete()
            Relationship.setRelRelationship(parent=branch, child=project, user=user)

        if current_company:
            Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=project, type='dependence', user=user)

        gallery.save(parent=project.id, user=user)
        pages.save(parent=project.id, user=user)

        project.reindexItem()

        func.notify("item_created", 'notification', user=user)


    trans_real.deactivate()
    return True

@transaction.atomic
def addBannerAttr(post, files, user, site_id, ids, bType):
    values = {}

    values['NAME'] = post.get('NAME', "")
    values['SITE_NAME'] = post.get('SITE_NAME', "")
    values['IMAGE'] = files.get('IMAGE', "")

    form = ItemForm('AdvBanner', values=values)
    form.clean()

    item = form.save(user, site_id, disableNotify=True)

    if not item:
        raise Exception('Error occurred while saving form')

    stDate = post.get('st_date')
    edDate = post.get('ed_date')

    stDate = datetime.datetime.strptime(stDate, "%m/%d/%Y")
    edDate = datetime.datetime.strptime(edDate, "%m/%d/%Y")

    Item.objects.filter(pk=item.pk).update(start_date=stDate, end_date=edDate)
    Relationship.setRelRelationship(parent=bType, child=item, type="relation", user=user)

    delta = edDate - stDate
    delta = delta.days

    costs = Item.getItemsAttributesValues('COST', ids)
    total = 0

    for id in ids:
        if not isinstance(costs[id], dict):
            costs[id] = {}

        cost = costs[id].get('COST', [0])[0]
        costs[id] = cost
        total += float(cost) * delta

    history = {
        'costs': costs,
        'ids': ids
    }

    history = json.dumps(history)

    advGoal = Item.objects.filter(pk__in=ids)
    bulk = []

    for goal in advGoal:
        bulk.append(Relationship(child=item, parent=goal, create_user=user, type="relation"))

    Relationship.objects.bulk_create(bulk)

    itemAttrs = item.getAttributeValues('IMAGE', 'SITE_NAME', 'NAME')

    attr = {
        'ORDER_HISTORY': history,
        'IMAGE': itemAttrs.get('IMAGE', [''])[0],
        'ORDER_DAYS': delta,
        'COST': total,
        'START_EVENT_DATE': stDate,
        'END_EVENT_DATE': edDate,
        'SITE_NAME': itemAttrs.get('SITE_NAME', [''])[0],
        'NAME': itemAttrs.get('NAME', [''])[0]
    }

    form = ItemForm('AdvOrder', values=attr)
    form.clean()

    ord = form.save(user, site_id, disableNotify=True)

    Relationship.setRelRelationship(item, ord, user=user, type="relation")


@transaction.atomic
def addTopAttr(post, object, user, site_id, ids):

    form = ItemForm('AdvTop', values={})
    form.clean()

    item = AdvTop(create_user=user)
    item.save()

    if not item:
        raise Exception('Error occurred while saving form')

    item.sites.add(site_id)

    stDate = post.get('st_date')
    edDate = post.get('ed_date')

    stDate = datetime.datetime.strptime(stDate, "%m/%d/%Y")
    edDate = datetime.datetime.strptime(edDate, "%m/%d/%Y")

    Item.objects.filter(pk=item.pk).update(start_date=stDate, end_date=edDate)
    Relationship.setRelRelationship(parent=item, child=object, type="relation", user=user)

    delta = edDate - stDate
    delta = delta.days

    costs = Item.getItemsAttributesValues('COST', ids)
    total = 0

    for id in ids:
        if not isinstance(costs[id], dict):
            costs[id] = {}

        cost = costs[id].get('COST', [0])[0]
        costs[id] = cost
        total += float(cost) * delta

    history = {
        'costs': costs,
        'ids': ids
    }

    history = json.dumps(history)

    advGoal = Item.objects.filter(pk__in=ids)
    bulk = []

    for goal in advGoal:
        bulk.append(Relationship(child=item, parent=goal, create_user=user, type="relation"))

    Relationship.objects.bulk_create(bulk)

    itemAttrs = object.getAttributeValues('NAME')

    attr = {
        'ORDER_HISTORY': history,
        'ORDER_DAYS': delta,
        'COST': total,
        'START_EVENT_DATE': stDate,
        'END_EVENT_DATE': edDate,
        'NAME': itemAttrs[0]
    }

    form = ItemForm('AdvOrder', values=attr)
    form.clean()

    ord = form.save(user, site_id, disableNotify=True)

    Relationship.setRelRelationship(item, ord, user=user, type="relation")

