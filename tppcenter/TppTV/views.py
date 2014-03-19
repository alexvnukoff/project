from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *

from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponseRedirect, HttpResponse
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship

from appl import func
from tppcenter.forms import ItemForm
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from haystack.query import SQ, SearchQuerySet
import json
from core.tasks import addTppAttrubute
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache

def get_news_list(request,page=1, item_id=None, slug=None):

 #   if slug and not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
  #       slug = Value.objects.get(item=item_id, attr__title='SLUG').title
   #      return HttpResponseRedirect(reverse('tv:detail',  args=[slug]))

    description = ''
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css']
    scripts = []



    if not item_id:
        attr = ('NAME', 'IMAGE', 'YOUTUBE_CODE', 'SLUG')
        newsPage = func.setContent(request, TppTV, attr, 'tv', 'TppTV/contentPage.html', 9, page=page)

    else:
        result = _getdetailcontent(request, item_id)
        newsPage = result[0]
        description = result[1]


    if not request.is_ajax():

        current_section = "TPP-TV"

        templatePramrams = {
            'current_section': current_section,
            'newsPage': newsPage,
            'scripts': scripts,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'current_company': current_company,
            'addNew': reverse('tv:add'),
            'cabinetValues': cabinetValues,
            'description': description
        }

        return render_to_response("TppTV/index.html", templatePramrams, context_instance=RequestContext(request))

    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage,
        }

        return HttpResponse(json.dumps(serialize))




@login_required(login_url='/login/')
def tvForm(request, action, item_id=None):

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    current_section = _("TppTv")

    if action == 'add':
        newsPage = addNews(request)
    else:
        newsPage = updateNew(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'formContent': newsPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))

def addNews(request):

    perm = request.user.get_all_permissions()

    if not {'appl.add_tpptv'}.issubset(perm):
         return func.permissionDenied()

    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')


    if request.POST:
        user = request.user

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('TppTV', values=values)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('tv:main'))

    template = loader.get_template('TppTV/addForm.html')
    context = RequestContext(request, {'form': form, 'categories': categories, 'countries': countries})
    newsPage = template.render(context)

    return newsPage



def updateNew(request, item_id):

    perm = request.user.get_all_permissions()

    if not {'appl.change_tpptv'}.issubset(perm) or not 'Redactor' in request.user.groups.values_list('name', flat=True):
          return func.permissionDenied()

    create_date = TppTV.objects.get(pk=item_id).create_date

    try:
        choosen_category = NewsCategories.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""

    countries = func.getItemsList("Country", 'NAME')
    categories = func.getItemsList('NewsCategories', 'NAME')

    if request.method != 'POST':
        form = ItemForm('TppTV', id=item_id)

    if request.POST:
        user = request.user


        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('TppTV', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addTppAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                  lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('tv:main'))


    template = loader.get_template('TppTV/addForm.html')

    templateParams = {
        'form': form,
        'choosen_category': choosen_category,
        'categories': categories,
        'create_date': create_date,
        'choosen_country':choosen_country,
        'countries': countries
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage




def _getdetailcontent(request, item_id):

    cache_name = "detail_%s" % item_id
    description_cache_name = "description_%s" % item_id
    cached = cache.get(cache_name)
    if not cached:

        new = get_object_or_404(TppTV, pk=item_id)
        newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE'))
        description = newValues.get('DETAIL_TEXT', False)[0] if newValues.get('DETAIL_TEXT', False) else ""
        description = func.cleanFromHtml(description)

        organizations = dict(Organization.objects.filter(p2c__child=new.pk).values('c2p__parent__country', 'pk'))

        try:
            newsCategory = NewsCategories.objects.get(p2c__child=item_id)
            category_value = newsCategory.getAttributeValues('NAME')
            newValues.update({'CATEGORY_NAME': category_value})
            similar_news = TppTV.objects.filter(c2p__parent__id=newsCategory.id).exclude(id=new.id)[:3]
            similar_news_ids = [sim_news.pk for sim_news in similar_news]
            similarValues = Item.getItemsAttributesValues(('NAME', 'DETAIL_TEXT', 'IMAGE', 'SLUG'), similar_news_ids)
        except ObjectDoesNotExist:
            similarValues = None
            pass


        if organizations.get('c2p__parent__country', False):
            countriesList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['c2p__parent__country'])
            toUpdate = {'COUNTRY_NAME': countriesList[organizations['c2p__parent__country']].get('NAME', [""]),
                        'COUNTRY_FLAG': countriesList[organizations['c2p__parent__country']].get('FLAG', [""]),
                        'COUNTRY_ID': organizations['c2p__parent__country']}

            newValues.update(toUpdate)


        if organizations.get('pk', False):
            organizationsList = Item.getItemsAttributesValues(('NAME', 'FLAG'), organizations['pk'])
            toUpdate = {'ORG_NAME': organizationsList[organizations['pk']].get('NAME', [""]),
                        'ORG_FLAG': organizationsList[organizations['pk']].get('FLAG', [""]),
                        'ORG_ID': organizations['pk']}

            newValues.update(toUpdate)



        template = loader.get_template('TppTV/detailContent.html')

        context = RequestContext(request, {'newValues': newValues, 'similarValues': similarValues})
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, description, 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        description = cache.get(description_cache_name)

    return rendered, description



