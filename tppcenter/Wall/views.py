from appl import func
from appl.models import InnovationProject, Product, BusinessProposal, Exhibition, News, Branch, NewsCategories
from core.models import Item
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

def get_wall_list(request):

    current_section = _("Wall")

    wallPage = _wallContent(request)

    templateParams = {
        'current_section': current_section,
        'wallPage': wallPage
    }

    return render_to_response("Wall/index.html", templateParams, context_instance=RequestContext(request))


def _wallContent(request):
    #------------------Innov--------------------------#
    innov_projects = list(InnovationProject.active.get_active().order_by('-pk').values_list('pk', flat=True)[:3])
    innovValues = Item.getItemsAttributesValues(('NAME', 'SLUG'), innov_projects)

    branches = Branch.objects.filter(p2c__child__in=innov_projects).values('p2c__child', 'pk')
    branches_ids = [branch['pk'] for branch in branches]
    branchesList = Item.getItemsAttributesValues(("NAME", 'COST', 'CURRENCY'), branches_ids)

    branches_dict = {}

    for branch in branches:
        branches_dict[branch['p2c__child']] = branch['pk']

    func.addDictinoryWithCountryAndOrganization(innov_projects, innovValues)

    for id, innov in innovValues.items():

        toUpdate = {
            'BRANCH_NAME': branchesList[branches_dict[id]].get('NAME', 0) if branches_dict.get(id, 0) else [0],
            'BRANCH_ID': branches_dict.get(id, 0)
        }

        innov.update(toUpdate)


    #----------------Product----------------------------#
    products = list(Product.active.get_active().order_by('-pk').values_list('pk', flat=True)[:4])
    productsValues = Item.getItemsAttributesValues(('NAME', 'IMAGE', 'COST', 'CURRENCY', 'SLUG'), products)
    func.addDictinoryWithCountryAndOrganization(products, productsValues)

    #---------------News---------------------------------#
    news = list(News.active.get_active().filter(c2p__parent__in=NewsCategories.objects.all()).order_by('-pk').values_list('pk', flat=True)[:3])
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

    templateParams = {
        'newsValues': newsValues,
        'exhibitionsValues': exhibitionsValues,
        'productsValues': productsValues,
        'innovValues': innovValues,
        'proposalsValues': proposalsValues
    }

    context = RequestContext(request, templateParams)

    return template.render(context)




