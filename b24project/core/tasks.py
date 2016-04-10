# -*- encoding: utf-8 -*-

import os

import boto3
from boto3.s3.transfer import S3Transfer
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils._os import abspathu

from b24online import utils
from b24online.models import B2BProduct, BusinessProposal, InnovationProject, News, Tender, Exhibition, \
    Organization
from b24online.utils import upload_to_S3

logger = get_task_logger('debug.core.tasks')

#from b24online.forms import ItemForm, BasePhotoGallery, BasePages, custom_field_callback
#from appl import func
#
#
# @shared_task
# ##@log_exception('News Task exception')
# def addNewsAttrubute(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
#     gallery = Photo(post, files)
#
#     timezoneInfo = get_current_timezone()
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     category = post.get('NEWS_CATEGORY', "")
#     category = NewsCategories.objects.get(pk=category) if category else False
#     country = post.get('COUNTRY', False)
#     country = Country.objects.get(pk=country) if country else False
#     date = post.get('CREATE_DATE', False)
#
#
#
#     form = ItemForm('News', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#     sizes = {
#             'big': {'box': (150, 140), 'fit': False},
#             'small': {'box': (70, 70), 'fit': False},
#             'th': {'box':(30, 30), 'fit': True}
#             }
#     new = form.save(user, site_id, sizes=sizes)
#     if new:
#         if date:
#             try:
#                 date = make_aware(datetime.datetime.strptime(date, "%m/%d/%Y"), timezoneInfo)
#                 new.create_date = date
#                 new.save()
#             except Exception as e:
#                 pass
#         gallery.save(parent=new.id, user=user)
#
#         if category:
#             Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
#             Relationship.setRelRelationship(parent=category, child=new, user=user)
#
#         if country:
#             Relationship.objects.filter(parent__in=Country.objects.all(), child=new.id).delete()
#             Relationship.setRelRelationship(parent=country, child=new, user=user)
#
#         if current_company:
#             Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=new, type='dependence', user=user)
#
#         new.reindexItem()
#
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
# @shared_task
# #@log_exception('Product Task exception')
# def addProductAttrubute(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
#     gallery = Photo(post, files)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, formfield_callback=custom_field_callback)
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#     categories = post.getlist('category[]')
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     start_date = post.get('START_DATE', None)
#     end_date = post.get('END_DATE', None)
#     #is_b2c_product = post.get('B2C_PRODUCT', None)
#
#     timezoneInfo = get_current_timezone()
#
#     if post.get('COUPON_DISCOUNT-END', None):
#        date = datetime.datetime.strptime(post.get('COUPON_DISCOUNT-END', None), "%m/%d/%Y")
#
#        date = make_aware(date, timezoneInfo)
#
#        edate = datetime.datetime.strptime(post.get('COUPON_DISCOUNT-START', None), "%m/%d/%Y") if post.get('COUPON_DISCOUNT-START', False) else now()
#
#        edate = make_aware(edate, timezoneInfo)
#
#        dates = {'COUPON_DISCOUNT': [edate, date]}
#     else:
#         dates = None
#
#
#
#     form = ItemForm('Product', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#     sizes = {
#             'big': {'box': (150, 140), 'fit': False},
#             'small': {'box': (60, 50), 'fit': False},
#             'th': {'box':(50, 40), 'fit': True}
#             }
#
#
#
#     product = form.save(user, site_id, dates=dates, sizes=sizes)
#
#     if product:
#         if end_date:
#             product.start_date = make_aware(datetime.datetime.strptime(start_date, "%m/%d/%Y"), timezoneInfo)
#             product.end_date = make_aware(datetime.datetime.strptime(end_date, "%m/%d/%Y"), timezoneInfo)
#             product.save()
#
#         if current_company:
#             parent = Organization.objects.get(pk=int(current_company))
#             Relationship.setRelRelationship(parent=parent, child=product, type='dependence', user=user)
#
#         Relationship.objects.filter(parent__in=Category.objects.all(), child=product).delete()
#
#         for cat in Category.objects.filter(pk__in=categories):
#             Relationship.setRelRelationship(parent=cat, child=product, user=user)
#
#
#         #site = Site.objects.get(name='centerpokupok')
#
#         #if is_b2c_product:
#          #   product.sites.all().delete()
#           #  product.sites.add(site.pk)
#         #else:
#          #   product.sites.remove(site.pk)
#           #  product.sites.add(Site.objects.get(name='b24online').pk)
#
#
#
#
#
#         gallery.save(parent=product.id, user=user)
#         pages.save(parent=product.id, user=user)
#         product.reindexItem()
#         func.notify("item_created", 'notification', user=user)
#
#
#     trans_real.deactivate()
#     return True
#
#
#
#
# @shared_task
# #@log_exception('Proposal Task exception')
# def addBusinessPRoposal(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
#     gallery = Photo(post, files)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, formfield_callback=custom_field_callback)
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     category = post.get('CATEGORY', None)
#
#
#     form = ItemForm('BusinessProposal', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#
#
#     proposal = form.save(user, site_id)
#     if proposal:
#
#         if branch:
#             branch = Branch.objects.get(pk=branch)
#             rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id)
#             Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id).delete()
#             Relationship.setRelRelationship(parent=branch, child=proposal, user=user)
#
#         if category:
#             category = BpCategories.objects.get(pk=category)
#             rel = Relationship.objects.filter(parent__in=BpCategories.objects.all(), child=proposal.id)
#             Relationship.objects.filter(parent__in=BpCategories.objects.all(), child=proposal.id).delete()
#             Relationship.setRelRelationship(parent=category, child=proposal, user=user)
#
#
#         if current_company:
#             Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=proposal, type='dependence', user=user)
#
#
#         gallery.save(parent=proposal.id, user=user)
#         pages.save(parent=proposal.id, user=user)
#         proposal.reindexItem()
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
# @shared_task
# #@log_exception('Company Task exception')
# def addNewCompany(post, files, user, site_id, addAttr=None, item_id=None, branch=None, lang_code=None):
#     trans_real.activate(lang_code)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     if post.get('Lat', ''):
#         values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')
#
#
#
#     country = post.get('COUNTRY', False)
#     country = Country.objects.get(pk=country) if country else False
#
#     tpp = post.get('TPP', False)
#     tpp = Tpp.objects.get(pk=tpp) if tpp else False
#
#     form = ItemForm('Company', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#     sizes = {
#             'big': {'box': (150, 140), 'fit': False},
#             'small': {'box': (70, 70), 'fit': False},
#             'th': {'box': (30, 30), 'fit': True}
#             }
#
#     company = form.save(user, site_id, sizes=sizes)
#     if company:
#
#         if branch:
#             branch = Branch.objects.get(pk=branch)
#             rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id)
#             Relationship.objects.filter(parent__in=Branch.objects.all(), child=company.id).delete()
#             Relationship.setRelRelationship(parent=branch, child=company, user=user)
#
#
#         if country:
#             Relationship.objects.filter(parent__in=Country.objects.all(), child=company.id).delete()
#             Relationship.setRelRelationship(parent=country, child=company, user=user, type='dependence')
#
#         if tpp:
#             Relationship.objects.filter(parent__in=Tpp.objects.all(), child=company.id).delete()
#             Relationship.setRelRelationship(parent=tpp, child=company, user=user)
#         else:
#             time = now() + datetime.timedelta(days=settings.FREE_PERIOD)
#             company.end_date = time
#             company.paid_till_date = time
#             company.save()
#
#         #this logic was moved into appl.models signal post_save from Department creation
#         #g = Group.objects.get(name=company.community)
#         #g.user_set.add(user)
#         pages.save(parent=company.id, user=user)
#         company.reindexItem()
#
#
#
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
#
# @shared_task
# #@log_exception('Tpp Task exception')
# def addTppAttrubute(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
#     trans_real.activate(lang_code)
#
#     values = {}
#     values['NAME'] = post.get('NAME', "")
#     values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
#     values['YOUTUBE_CODE'] = post.get('YOUTUBE_CODE', "")
#     values['IMAGE'] = files.get('IMAGE', "")
#     values['IMAGE-CLEAR'] = post.get('IMAGE-CLEAR', " ")
#     category = post.get('NEWS_CATEGORY', "")
#     category = NewsCategories.objects.get(pk=category) if category else False
#     date = post.get('CREATE_DATE', False)
#     country = post.get('COUNTRY', False)
#     country = Country.objects.get(pk=country) if country else False
#
#
#     form = ItemForm('TppTV', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#     sizes = {
#             'big': {'box': (150, 140), 'fit': False},
#             'small': {'box': (120, 90), 'fit': False},
#             'th': {'box':(60, 40), 'fit': True}
#             }
#
#     new = form.save(user, site_id, sizes=sizes)
#     if new:
#         if date:
#             try:
#
#                 timezoneInfo = get_current_timezone()
#                 date = make_aware(datetime.datetime.strptime(date, "%m/%d/%Y"), timezoneInfo)
#
#                 new.create_date = date
#                 new.save()
#             except Exception as e:
#                 pass
#
#
#         if category:
#             Relationship.objects.filter(parent__in=NewsCategories.objects.all(), child=new.id).delete()
#             Relationship.setRelRelationship(parent=category, child=new, user=user)
#
#         if country:
#             Relationship.objects.filter(parent__in=Country.objects.all(), child=new.id).delete()
#             Relationship.setRelRelationship(parent=country, child=new, user=user)
#
#         new.reindexItem()
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
#
# @shared_task
# #@log_exception('Tpp news Task exception')
# def addNewTpp(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
#     trans_real.activate(lang_code)
#     timezoneInfo = get_current_timezone()
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, fields=("content", 'title'))
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     if post.get('Lat', ''):
#         values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')
#
#     start_date = post.get('START_DATE', None)
#     end_date = post.get('END_DATE', None)
#
#     country = post.get('COUNTRY', False)
#     country = Country.objects.get(pk=country) if country else False
#
#
#     form = ItemForm('Tpp', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#     sizes = {
#             'big': {'box': (150, 140), 'fit': False},
#             'small': {'box': (70, 70), 'fit': False},
#             'th': {'box':(30, 30), 'fit': True}
#             }
#
#     tpp = form.save(user, site_id, sizes=sizes)
#
#     if tpp:
#         if end_date:
#             tpp.start_date = make_aware(datetime.datetime.strptime(start_date, "%m/%d/%Y"), timezoneInfo)
#             tpp.end_date = make_aware(datetime.datetime.strptime(end_date, "%m/%d/%Y"), timezoneInfo)
#             tpp.save()
#
#
#
#
#
#         if country:
#             Relationship.objects.filter(parent__in=Country.objects.all(), child=tpp.id).delete()
#             Relationship.setRelRelationship(parent=country, child=tpp, user=user, type='dependence')
#
#         pages.save(parent=tpp.id, user=user)
#
#         tpp.reindexItem()
#
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
# @shared_task
# #@log_exception('Tender Task exception')
# def addNewTender(post, files, user, site_id, addAttr=None, item_id=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
#     gallery = Photo(post, files)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, formfield_callback=custom_field_callback)
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     form = ItemForm('Tender', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#
#
#     tender = form.save(user, site_id)
#     if tender:
#         if current_company:
#             Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=tender, type='dependence', user=user)
#
#
#
#         tender.reindexItem()
#
#
#
#         gallery.save(parent=tender.id, user=user)
#         pages.save(parent=tender.id, user=user)
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
# @shared_task
# #@log_exception('Resume Task exception')
# def addNewResume(post, files, user, site_id, addAttr=None, item_id=None, lang_code=None):
#     trans_real.activate(lang_code)
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     form = ItemForm('Resume', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#     resume = form.save(user, site_id)
#     if resume:
#         relationship = Relationship.objects.filter(child=resume)
#         if not relationship.exists():
#             Relationship.setRelRelationship(parent=Cabinet.objects.get(user=user), child=resume, type='dependence', user=user)
#
#
#         resume.reindexItem()
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
#
# @shared_task
# #@log_exception('Exhibition Task exception')
# def addNewExhibition(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
#     gallery = Photo(post, files)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, formfield_callback=custom_field_callback)
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     if post.get('Lat', ''):
#         values['POSITION'] = post.get('Lat', '') + ',' + post.get('Lng')
#
#     country = post.get('COUNTRY', False)
#     country = Country.objects.get(pk=country) if country else False
#
#
#
#
#
#
#     form = ItemForm('Exhibition', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#
#
#     proposal = form.save(user, site_id)
#     if proposal:
#
#         if branch:
#             branch = Branch.objects.get(pk=branch)
#             rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id)
#             Relationship.objects.filter(parent__in=Branch.objects.all(), child=proposal.id).delete()
#             Relationship.setRelRelationship(parent=branch, child=proposal, user=user)
#
#
#         if current_company:
#             Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=proposal, type='dependence', user=user)
#
#
#         if country:
#             Relationship.objects.filter(parent__in=Country.objects.all(), child=proposal.id).delete()
#             Relationship.setRelRelationship(parent=country, child=proposal, user=user, type='relation')
#
#
#
#         proposal.reindexItem()
#
#
#
#
#         gallery.save(parent=proposal.id, user=user)
#         pages.save(parent=proposal.id, user=user)
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
# @shared_task
# #@log_exception('Requirement Task exception')
# def addNewRequirement(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#
#
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     vacancy = post.get('VACANCY', False)
#
#
#
#
#
#     form = ItemForm('Requirement', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#
#
#     requirement = form.save(user, site_id)
#     if requirement:
#
#         if vacancy:
#             Relationship.objects.filter(child=requirement, type='dependence').delete()
#             Relationship.setRelRelationship(parent=Vacancy.objects.get(pk=int(vacancy)), child=requirement, type='dependence', user=user)
#
#
#
#
#
#             requirement.reindexItem()
#
#
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
#
#
#
# @shared_task
# #@log_exception('Innovation project Task exception')
# def addNewProject(post, files, user, site_id, addAttr=None, item_id=None, branch=None, current_company=None, lang_code=None):
#     trans_real.activate(lang_code)
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
#     gallery = Photo(post, files)
#
#     Page = modelformset_factory(AdditionalPages, formset=BasePages, extra=10, formfield_callback=custom_field_callback)
#     pages = Page(post, files, prefix="pages")
#     pages.clean()
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#     form = ItemForm('InnovationProject', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#     project = form.save(user, site_id)
#
#     if project:
#         if branch:
#             branch = Branch.objects.get(pk=branch)
#             rel = Relationship.objects.filter(parent__in=Branch.objects.all(), child=project.id)
#             Relationship.objects.filter(parent__in=Branch.objects.all(), child=project.id).delete()
#             Relationship.setRelRelationship(parent=branch, child=project, user=user)
#
#         if current_company:
#             Relationship.setRelRelationship(parent=Organization.objects.get(pk=int(current_company)), child=project, type='dependence', user=user)
#
#         gallery.save(parent=project.id, user=user)
#         pages.save(parent=project.id, user=user)
#
#         project.reindexItem()
#
#         func.notify("item_created", 'notification', user=user)
#
#
#     trans_real.deactivate()
#     return True
#
# @transaction.atomic
# def addBannerAttr(post, files, user, site_id, ids, bType, current_company, factor):
#     values = {}
#
#     values['NAME'] = post.get('NAME', "")
#     values['SITE_NAME'] = post.get('SITE_NAME', "")
#     values['IMAGE'] = files.get('IMAGE', "")
#
#     stDate = post.get('st_date')
#     edDate = post.get('ed_date')
#
#     stDate = datetime.datetime.strptime(stDate, "%m/%d/%Y")
#     edDate = datetime.datetime.strptime(edDate, "%m/%d/%Y")
#
#     values['START_EVENT_DATE'] = stDate
#     values['END_EVENT_DATE'] = edDate
#
#     delta = edDate - stDate
#     delta = delta.days
#
#     costs = Item.getItemsAttributesValues('COST', ids)
#     total = 0
#
#     for id in ids:
#         if not isinstance(costs[id], dict):
#             costs[id] = {}
#
#         cost = costs[id].get('COST', [0])[0]
#         costs[id] = cost
#         total += float(cost) * delta * factor
#
#     values['COST'] = total
#
#     form = ItemForm('AdvBanner', values=values)
#     form.clean()
#
#     item = form.save(user, site_id, disableNotify=True)
#
#     if not item:
#         raise Exception('Error occurred while saving form')
#
#     timezoneInfo = get_current_timezone()
#     stDate = make_aware(stDate, timezoneInfo)
#
#     Item.objects.filter(pk=item.pk).update(start_date=stDate, end_date=now())
#     Relationship.setRelRelationship(parent=bType, child=item, type="relation", user=user)
#
#
#     if current_company:
#         dep = Item.objects.get(pk=current_company)
#     else:
#         dep = Cabinet.objects.get(user=user)
#
#
#     history = {
#         'costs': costs,
#         'ids': ids,
#         'owner_id': dep.pk,
#         'owner': dep.getName()
#     }
#
#     history = json.dumps(history)
#
#     advGoal = Item.objects.filter(pk__in=ids)
#
#     for goal in advGoal:
#         Relationship.setRelRelationship(goal, item, user=user, type="relation")
#
#
#     itemAttrs = item.getAttributeValues('IMAGE', 'SITE_NAME', 'NAME')
#
#     attr = {
#         'ORDER_HISTORY': history,
#         'IMAGE': itemAttrs.get('IMAGE', [''])[0],
#         'ORDER_DAYS': delta,
#         'COST': total,
#         'START_EVENT_DATE': stDate,
#         'END_EVENT_DATE': edDate,
#         'SITE_NAME': itemAttrs.get('SITE_NAME', [''])[0],
#         'NAME': itemAttrs.get('NAME', [''])[0]
#     }
#
#     form = ItemForm('AdvOrder', values=attr)
#     form.clean()
#     sizes = {
#             'big': {'box': (200, 100), 'fit': False},
#
#             }
#
#     ord = form.save(user, site_id, disableNotify=True, sizes=sizes)
#
#     Relationship.setRelRelationship(item, ord, user=user, type="relation")
#     Relationship.setRelRelationship(dep, item, user=user, type="dependence")
#     Relationship.setRelRelationship(dep, ord, user=user, type="relation")
#
#     return ord.pk
#
#
# @transaction.atomic
# def addTopAttr(post, object, user, site_id, ids, org, factor):
#
#     stDate = post.get('st_date')
#     edDate = post.get('ed_date')
#
#     stDate = datetime.datetime.strptime(stDate, "%m/%d/%Y")
#     edDate = datetime.datetime.strptime(edDate, "%m/%d/%Y")
#
#     delta = edDate - stDate
#     delta = delta.days
#
#     costs = Item.getItemsAttributesValues('COST', ids)
#     total = 0
#
#     for id in ids:
#         if not isinstance(costs[id], dict):
#             costs[id] = {}
#
#         cost = costs[id].get('COST', [0])[0]
#         costs[id] = cost
#         total += float(cost) * delta
#
#     values = {
#         'COST': total,
#         'START_EVENT_DATE': stDate,
#         'END_EVENT_DATE': edDate
#     }
#
#     form = ItemForm('AdvTop', values=values)
#     form.clean()
#
#     item = form.save(user, site_id, disableNotify=True)
#
#     if not item:
#         raise Exception('Error occurred while saving form')
#
#     #item.sites.add(site_id)
#
#     timezoneInfo = get_current_timezone()
#
#     stDate = make_aware(stDate, timezoneInfo)
#
#     Item.objects.filter(pk=item.pk).update(start_date=stDate, end_date=now())
#     Relationship.setRelRelationship(object, item, user=user, type="dependence")
#
#     history = {
#         'costs': costs,
#         'ids': ids,
#         'owner_id': org.pk,
#         'owner': org.getName()
#     }
#
#     history = json.dumps(history)
#
#     advGoal = Item.objects.filter(pk__in=ids)
#
#     for goal in advGoal:
#         Relationship.setRelRelationship(goal, item, user=user, type="relation")
#
#     itemAttrs = object.getAttributeValues('NAME')
#
#     attr = {
#         'ORDER_HISTORY': history,
#         'ORDER_DAYS': delta,
#         'COST': total,
#         'START_EVENT_DATE': stDate,
#         'END_EVENT_DATE': edDate,
#         'NAME': itemAttrs[0]
#     }
#
#     form = ItemForm('AdvOrder', values=attr)
#     form.clean()
#
#     ord = form.save(user, site_id, disableNotify=True)
#
#     Relationship.setRelRelationship(item, ord, user=user, type="relation")
#     Relationship.setRelRelationship(org, ord, user=user, type="relation")
#
#     return ord.pk
#
#
# @shared_task
# #@log_exception('External site Task exception')
# def addNewSite(post, files, user, company_id,  addAttr=None,  item_id=None, lang_code=None):
#     trans_real.activate(lang_code)
#
#     Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
#     gallery = Photo(post, files)
#
#     values = {}
#     values.update(post)
#     values.update(files)
#
#
#     form = ItemForm('UserSites', values=values, id=item_id, addAttr=addAttr)
#     form.clean()
#
#     if form.is_valid():
#         sub = values['NAME'][0].lower()
#         site, created = Site.objects.get_or_create(domain=sub + '.' + settings.USER_SITES_DOMAIN, name='usersites')
#         user_site = form.save(user, site.pk)
#         if user_site:
#             user_site.organization = Organization.objects.get(pk=company_id)
#             user_site.save()
#             user_site.sites.add(site.pk)
#             user_site.sites.all().exclude(pk=site.pk).delete()
#
#             gallery.save(parent=user_site.id, user=user)
#         else:
#             if created:
#                 site.delete()
#
#
#
#         func.notify("item_created", 'notification', user=user)
#
#     trans_real.deactivate()
#     return True
#
from centerpokupok.models import B2CProduct
from jobs.models import Requirement
from usersites.models import UserSite


@shared_task
def upload_file(*args):
    upload_to_S3(*args)


@shared_task
def upload_images(*args, async=True):
    images = []
    for image in args:
        abs_path = abspathu(settings.MEDIA_ROOT)

        if abs_path in image['file']:
            bucket_path = image['file'][len(abs_path):]
        else:
            bucket_path = image['file']

        bucket_path = bucket_path.replace('\\', '/')

        filename = os.path.basename(image['file'])
        filepath = os.path.dirname(image['file'])

        if 'sizes' in image:
            for size_name, size_data in image['sizes'].items():
                resize_name = "%s_%s" % (size_name, filename)
                out = (os.path.join(filepath, resize_name)).replace('\\', '/')
                utils.resize(image['file'], out=out, **size_data)
                images.append({
                    'file': out,
                    'bucket_path': "%s%s" % (size_name, bucket_path),
                    'content_type': 'image/png',
                })

        images.append({
            'file': image['file'],
            'bucket_path': "original%s" % bucket_path,
            'content_type': 'image/png'
        })

        upload_to_S3(*images)


@shared_task
def on_company_active_changed(org_id):
    org = Organization.objects.get(pk=org_id)
    querysets = (
        B2BProduct.objects.filter(company=org).exclude(is_active=not org.is_deleted),
        B2CProduct.objects.filter(company=org).exclude(is_active=not org.is_deleted),
        UserSite.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        BusinessProposal.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        InnovationProject.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        News.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Tender.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Exhibition.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Requirement.objects.filter(vacancy__department__organization=org).exclude(is_active=not org.is_deleted)
    )

    for queryset in querysets:
        objects_to_reindex = list(queryset)
        updated = queryset.update(is_active=not org.is_deleted)

        if updated > 0:
            for obj in objects_to_reindex:
                reindex_method = getattr(obj, 'reindex', None)

                if reindex_method is not None:
                    reindex_method(is_active_changed=True)


@shared_task
def on_chamber_active_changed(org_id):
    org = Organization.objects.get(pk=org_id)
    querysets = (
        UserSite.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        BusinessProposal.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        InnovationProject.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        News.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Tender.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Exhibition.objects.filter(organization=org).exclude(is_active=not org.is_deleted),
        Requirement.objects.filter(organization=org).exclude(is_active=not org.is_deleted)
    )

    for queryset in querysets:
        updated = queryset.update(is_active=not org.is_deleted)

        if updated > 0:
            for obj in queryset:
                reindex_method = getattr(obj, 'reindex', None)

                if reindex_method is not None:
                    reindex_method(is_active_changed=True)
