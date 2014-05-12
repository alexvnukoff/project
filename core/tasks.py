from django.db import transaction
from appl.models import *
from django.utils.translation import trans_real
from django.forms.models import modelformset_factory
from django.contrib.sites.models import Site
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.contrib.sites.models import Site
from celery import shared_task, task
import json
from appl import func


@shared_task
def addNewsAttrubute(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    values = {}
    values.update(post)
    values.update(files)

    category = post.get('NEWS_CATEGORY', "")
    category = NewsCategories.objects.get(pk=category) if category else False
    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False
    date = post.get('CREATE_DATE', False)



    form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
    form.clean()
    sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (70, 70), 'fit': False},
            'th': {'box':(30, 30), 'fit': True}
            }
    new = form.save(user, site_id, sizes=sizes)
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


    values = {}
    values.update(post)
    values.update(files)

    start_date = post.get('START_DATE', None)
    end_date = post.get('END_DATE', None)
    category = post.get('CATEGORY', None)
    is_b2c_product = post.get('B2C_PRODUCT', None)

    if post.get('COUPON_DISCOUNT-END', None):
       date = datetime.datetime.strptime(post.get('COUPON_DISCOUNT-END', None), "%m/%d/%Y")
       edate = datetime.datetime.strptime(post.get('COUPON_DISCOUNT-START', None), "%m/%d/%Y") if post.get('COUPON_DISCOUNT-START', False) else now()
       dates = {'COUPON_DISCOUNT': [edate, date]}
    else:
        dates = None



    form = ItemForm('Product', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (60, 50), 'fit': False},
            'th': {'box':(50, 40), 'fit': True}
            }

    product = form.save(user, site_id, dates=dates, sizes=sizes)
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

        site = Site.objects.get(name='centerpokupok')

        if is_b2c_product:
            product.sites.all().delete()
            product.sites.add(site.pk)
        else:
            product.sites.remove(site.pk)
            product.sites.add(Site.objects.get(name='tppcenter').pk)





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

    values = {}
    values.update(post)
    values.update(files)


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


    values = {}
    values.update(post)
    values.update(files)

    if post.get('Lat', ''):
        values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')



    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False

    tpp = post.get('TPP', False)
    tpp = Tpp.objects.get(pk=tpp) if tpp else False

    form = ItemForm('Company', values=values, id=item_id, addAttr=addAttr)
    form.clean()
    sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (70, 70), 'fit': False},
            'th': {'box':(30, 30), 'fit': True}
            }

    company = form.save(user, site_id, sizes=sizes)
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

        #this logic was moved into appl.models signal post_save from Department creation
        #g = Group.objects.get(name=company.community)
        #g.user_set.add(user)
        company.reindexItem()




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
    sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (120, 90), 'fit': False},
            'th': {'box':(60, 40), 'fit': True}
            }

    new = form.save(user, site_id, sizes=sizes)
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


    values = {}
    values.update(post)
    values.update(files)

    if post.get('Lat', ''):
        values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')

    start_date = post.get('START_DATE', None)
    end_date = post.get('END_DATE', None)

    country = post.get('COUNTRY', False)
    country = Country.objects.get(pk=country) if country else False

    form = ItemForm('Tpp', values=values, id=item_id, addAttr=addAttr)
    form.clean()
    sizes = {
            'big': {'box': (150, 140), 'fit': False},
            'small': {'box': (70, 70), 'fit': False},
            'th': {'box':(30, 30), 'fit': True}
            }

    tpp = form.save(user, site_id, sizes=sizes)
    if tpp:
        if end_date:
            tpp.start_date = datetime.datetime.strptime(start_date, "%m/%d/%Y")
            tpp.end_date = datetime.datetime.strptime(end_date, "%m/%d/%Y")
            tpp.save()





        if country:
            Relationship.objects.filter(parent__in=Country.objects.all(), child=tpp.id).delete()
            Relationship.setRelRelationship(parent=country, child=tpp, user=user, type='dependence')

        tpp.reindexItem()


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


    values = {}
    values.update(post)
    values.update(files)

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
def addNewResume(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
    trans_real.activate(lang_code)

    values = {}
    values.update(post)
    values.update(files)

    form = ItemForm('Resume', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    resume = form.save(user, site_id)
    if resume:
        Relationship.objects.filter(parent=Cabinet.objects.get(user=user), child=resume).delete()
        Relationship.setRelRelationship(parent=Cabinet.objects.get(user=user), child=resume, type='dependence', user=user)




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


    values = {}
    values.update(post)
    values.update(files)

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
def addNewRequirement(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
    trans_real.activate(lang_code)



    values = {}
    values.update(post)
    values.update(files)

    vacancy = post.get('VACANCY', False)





    form = ItemForm('Requirement', values=values, id=item_id, addAttr=addAttr)
    form.clean()



    requirement = form.save(user, site_id)
    if requirement:

        if vacancy:
            Relationship.objects.filter(child=requirement, type='dependence').delete()
            Relationship.setRelRelationship(parent=Vacancy.objects.get(pk=int(vacancy)), child=requirement, type='dependence', user=user)









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

    values = {}
    values.update(post)
    values.update(files)

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
def addBannerAttr(post, files, user, site_id, ids, bType, current_company):
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

    if current_company:
        dep = Item.objects.get(pk=current_company)
    else:
        dep = Cabinet.objects.get(user=user)


    history = {
        'costs': costs,
        'ids': ids,
        'owner_id': dep.pk,
        'owner': dep.getName()
    }

    history = json.dumps(history)

    advGoal = Item.objects.filter(pk__in=ids)

    for goal in advGoal:
        Relationship.setRelRelationship(goal, item, user=user, type="relation")


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
    sizes = {
            'big': {'box': (200, 100), 'fit': False},

            }

    ord = form.save(user, site_id, disableNotify=True, sizes=sizes)

    Relationship.setRelRelationship(item, ord, user=user, type="relation")
    Relationship.setRelRelationship(dep, item, user=user, type="dependence")
    Relationship.setRelRelationship(dep, ord, user=user, type="relation")


@transaction.atomic
def addTopAttr(post, object, user, site_id, ids, org):

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
    Relationship.setRelRelationship(object, item, user=user, type="dependence")

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
        'ids': ids,
        'owner_id': org.pk,
        'owner': org.getName()
    }

    history = json.dumps(history)

    advGoal = Item.objects.filter(pk__in=ids)

    for goal in advGoal:
        Relationship.setRelRelationship(goal, item, user=user, type="relation")

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
    Relationship.setRelRelationship(org, ord, user=user, type="relation")



def addNewSite(post, files, user, company_id,  addAttr=None,  item_id=None, lang_code=None):
    trans_real.activate(lang_code)

    values = {}
    values.update(post)
    values.update(files)


    form = ItemForm('UserSites', values=values, id=item_id, addAttr=addAttr)
    form.clean()

    if form.is_valid():
        site, created = Site.objects.get_or_create(domain=values['NAME'][0] +'.tppcenter.com', name='usersites')
        user_site = form.save(user, site.pk)
        if user_site:
            user_site.organization = Organization.objects.get(pk=company_id)
            user_site.save()
            user_site.sites.add(site.pk)
            user_site.sites.all().exclude(pk=site.pk).delete()
        else:
            if created:
                site.delete()


        func.notify("item_created", 'notification', user=user)

    trans_real.deactivate()
    return True
