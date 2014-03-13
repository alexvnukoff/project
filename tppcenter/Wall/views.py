from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from core.tasks import addTppAttrubute
from django.conf import settings

def get_wall_list(request):


    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    user = request.user


    current_section = _("Wall")


    wallPage = _wallContent(request)


    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')
    tops = func.getTops(request)

    templateParams = {

        'current_section': current_section,
        'wallPage': wallPage,
        'current_company': current_company,
        'cabinetValues': cabinetValues,
        'bannerRight': bRight,
        'bannerLeft': bLeft,
        'tops': tops
    }


    return render_to_response("Wall/index.html", templateParams, context_instance=RequestContext(request))


def _wallContent(request):
    #------------------Innov--------------------------#
    innov_projects = list(InnovationProject.active.get_active().order_by('-pk').values_list('pk', flat=True)[:3])
    innovValues = Item.getItemsAttributesValues(('NAME', 'SLUG'), innov_projects)

    branches = Branch.objects.filter(p2c__child__in=innov_projects).values('p2c__child', 'pk')
    branches_ids = [branch['pk'] for branch in branches]
    branchesList = Item.getItemsAttributesValues(("NAME"), branches_ids)

    branches_dict = {}
    for branch in branches:
        branches_dict[branch['p2c__child']] = branch['pk']

    func.addDictinoryWithCountryAndOrganization(innov_projects, innovValues)

    for id, innov in innovValues.items():

        toUpdate = {'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0) if branches_dict.get(id, 0) else [0],
                    'BRANCH_ID': branches_dict.get(id, 0)}
        innov.update(toUpdate)


    #----------------Product----------------------------#
    products = list(Product.active.get_active().order_by('-pk').values_list('pk', flat=True)[:4])
    productsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), products)
    func.addDictinoryWithCountryAndOrganization(products, productsValues)

    #---------------News---------------------------------#
    news = list(News.active.get_active().order_by('-pk').values_list('pk', flat=True)[:3])
    newsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), news)
    func.addDictinoryWithCountryAndOrganization(news, newsValues)


    #---------------BusinessProposal--------------------#
    proposals = list(BusinessProposal.active.get_active().order_by('-pk').values_list('pk', flat=True)[:3])
    proposalsValues = Item.getItemsAttributesValues(('NAME', 'SLUG'), proposals)
    func.addDictinoryWithCountryAndOrganization(proposals, proposalsValues)


    #--------------Exhibitions--------------------------#
    exhibitions = list(Exhibition.active.get_active().order_by('-pk').values_list('pk', flat=True)[:3])
    exhibitionsValues = Item.getItemsAttributesValues(('NAME', 'CITY', 'COUNTRY', 'START_EVENT_DATE',
                                                       'END_EVENT_DATE', 'SLUG'), exhibitions)
    func.addDictinoryWithCountryAndOrganization(exhibitions, exhibitionsValues)


    template = loader.get_template('Wall/contentPage.html')

    context = RequestContext(request, {'newsValues': newsValues, 'exhibitionsValues': exhibitionsValues,
                                       'productsValues': productsValues, 'innovValues': innovValues,
                                       'proposalsValues': proposalsValues})
    return template.render(context)




