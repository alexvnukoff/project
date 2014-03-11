from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
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
from haystack.query import SQ, SearchQuerySet
import json
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime


from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request, page=1, my=None):

    filterAdv = []

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")
    try:
        newsPage, filterAdv = _newsContent(request, page, my)

    except ObjectDoesNotExist:
        return render_to_response("permissionDen.html")

    cabinetValues = func.getB2BcabinetValues(request)
    styles = []
    scripts = []

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    tops = func.getTops(request, {Product: 5, InnovationProject: 5, Company: 5, BusinessProposal: 5}, filter=filterAdv)

    if not request.is_ajax():
        user = request.user
        if user.is_authenticated():
            notification = Notification.objects.filter(user=request.user, read=False).count()
            if not user.first_name and not user.last_name:
                user_name = user.email
            else:
                user_name = user.first_name + ' ' + user.last_name
        else:
            user_name = None
            notification = None
        current_section = _("News")

        templateParams = {
            'user_name': user_name,
            'current_section': current_section,
            'notification': notification,
            'newsPage': newsPage,
            'scripts': scripts,
            'current_company': current_company,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'addNew': reverse('news:add'),
            'cabinetValues': cabinetValues,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return render_to_response("News/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage,
            'bannerRight': bRight,
            'bannerLeft': bLeft,
            'tops': tops
        }

        return HttpResponse(json.dumps(serialize))

def _newsContent(request, page=1, my=None):

    filterAdv = []

    if not my:
        filters, searchFilter, filterAdv = func.filterLive(request)

        #news = News.active.get_active().order_by('-pk')

        sqs = SearchQuerySet().models(News).filter(SQ(obj_end_date__gt=timezone.now())| SQ(obj_end_date__exact=datetime(1 , 1, 1)),
                                                               obj_start_date__lt=timezone.now())

        if len(searchFilter) > 0:
            sqs = sqs.filter(**searchFilter)

        q = request.GET.get('q', '')

        if q != '':
            sqs = sqs.filter(SQ(title=q) | SQ(text=q))

        sortFields = {
            'date': 'id',
            'name': 'title'
        }

        order = []

        sortField1 = request.GET.get('sortField1', 'date')
        sortField2 = request.GET.get('sortField2', None)
        order1 = request.GET.get('order1', 'desc')
        order2 = request.GET.get('order2', None)

        if sortField1 and sortField1 in sortFields:
            if order1 == 'desc':
                order.append('-' + sortFields[sortField1])
            else:
                order.append(sortFields[sortField1])
        else:
            order.append('-id')

        if sortField2 and sortField2 in sortFields:
            if order2 == 'desc':
                order.append('-' + sortFields[sortField2])
            else:
                order.append(sortFields[sortField2])

        news = sqs.order_by(*order)
        url_paginator = "news:paginator"
        params = {'filters': filters,
                  'sortField1': sortField1,
                  'sortField2': sortField2,
                  'order1': order1,
                  'order2': order2}
    else:

        current_organization = request.session.get('current_company', False)

        if current_organization:
             news = SearchQuerySet().models(News).\
                 filter(SQ(tpp=current_organization)|SQ(company=current_organization))

             url_paginator = "news:my_main_paginator"
             params = {}
        else:
             raise ObjectDoesNotExist('you need check company')

    result = func.setPaginationForSearchWithValues(news, *('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), page_num=5, page=page)
    #result = func.setPaginationForItemsWithValues(news, *('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG'), page_num=5, page=page)

    newsList = result[0]
    news_ids = [id for id in newsList.keys()]

    func.addDictinoryWithCountryAndOrganization(news_ids, newsList)

    page = result[1]
    paginator_range = func.getPaginatorRange(page)




    template = loader.get_template('News/contentPage.html')

    templateParams = {
        'newsList': newsList,
        'page': page,
        'paginator_range': paginator_range,
        'url_paginator': url_paginator,

    }
    templateParams.update(params)

    context = RequestContext(request, templateParams)

    return template.render(context), filterAdv

@login_required(login_url='/login/')
def newsForm(request, action, item_id=None):
    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)
    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")


    user = request.user

    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()

        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name

    else:

        user_name = None
        notification = None

    current_section = _("News")

    if action == 'add':
        newsPage = addNews(request)
    else:
        newsPage = updateNew(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    return render_to_response('News/index.html', {'newsPage': newsPage, 'current_company':current_company,
                                                              'notification': notification, 'user_name': user_name,
                                                              'current_section': current_section,
                                                              'cabinetValues': cabinetValues},
                              context_instance=RequestContext(request))


def addNews(request):
    current_company = request.session.get('current_company', None)

    if current_company:
        item = Organization.objects.get(pk=current_company)
        perm_list = item.getItemInstPermList(request.user)
        if 'add_news' not in perm_list:
             return render_to_response("permissionDenied.html")
    else:
        perm = request.user.get_all_permissions()
        if not {'appl.add_news'}.issubset(perm):
            return render_to_response("permissionDenied.html")


    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')



    if request.POST:

        user = request.user
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")


        form = ItemForm('News', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('news:main'))



    template = loader.get_template('News/addForm.html')
    context = RequestContext(request, {'form': form, 'categories': categories, 'countries': countries})
    newsPage = template.render(context)


    return newsPage



def updateNew(request, item_id):

    try:
        item = Organization.objects.get(p2c__child_id=item_id)
        perm_list = item.getItemInstPermList(request.user)
        if 'change_news' not in perm_list:
            raise PermissionError('permission denied')
    except Exception:
         perm = request.user.get_all_permissions()
         if not {'appl.change_news'}.issubset(perm) or not 'Redactor' in request.user.groups.values_list('name', flat=True):
             return render_to_response("permissionDenied.html")




    create_date = News.objects.get(pk=item_id).create_date

    try:
        choosen_category = NewsCategories.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    try:
        choosen_country = Country.objects.get(p2c__child__id=item_id)
    except ObjectDoesNotExist:
        choosen_country = ""
    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')
    if request.method != 'POST':
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(parent_id=item_id)
        photos = ""

        if gallery.queryset:
            photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]


        form = ItemForm('News', id=item_id)

    if request.POST:


        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values['NAME'] = request.POST.get('NAME', "")
        values['DETAIL_TEXT'] = request.POST.get('DETAIL_TEXT', "")
        values['YOUTUBE_CODE'] = request.POST.get('YOUTUBE_CODE', "")
        values['IMAGE'] = request.FILES.get('IMAGE', "")
        values['IMAGE-CLEAR'] = request.POST.get('IMAGE-CLEAR', " ")

        form = ItemForm('News', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id, lang_code=settings.LANGUAGE_CODE)
            return HttpResponseRedirect(reverse('news:main'))



    template = loader.get_template('News/addForm.html')
    context = RequestContext(request, {'gallery': gallery, 'photos': photos, 'form': form,
                                                    'choosen_category': choosen_category, 'categories': categories,
                                                    'countries': countries, 'choosen_country': choosen_country,
                                                    'create_date':create_date})
    newsPage = template.render(context)




    return newsPage



def detail(request, item_id, slug=None):

    filterAdv = func.getDeatailAdv(item_id)

    if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
         slug = Value.objects.get(item=item_id, attr__title='SLUG').title
         return HttpResponseRedirect(reverse('news:detail',  args=[slug]))

    styles = [settings.STATIC_URL + 'tppcenter/css/news.css', settings.STATIC_URL + 'tppcenter/css/company.css']
    scripts = []

    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "News"



    newsPage = _getdetailcontent(request, item_id)


    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html', filter=filterAdv)
    tops = func.getTops(request, {Product: 5, InnovationProject: 5, Company: 5, BusinessProposal: 5}, filter=filterAdv)

    templateParams = {
        'user_name': user_name,
        'current_section': current_section,
        'newsPage': newsPage,
        'notification': notification,
        'styles': styles,
        'scripts': scripts,
        'addNew': reverse('news:add'),
        'bRight': bRight,
        'bLeft': bLeft,
        'tops': tops
    }



    return render_to_response("News/index.html", templateParams, context_instance=RequestContext(request))



def _getdetailcontent(request, id):
    new = get_object_or_404(News, pk=id)
    newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE', 'IMAGE'))
    photos = Gallery.objects.filter(c2p__parent=new)




    try:
        newsCategory = NewsCategories.objects.get(p2c__child=id)
        category_value = newsCategory.getAttributeValues('NAME')
        newValues.update({'CATEGORY_NAME': category_value})
        similar_news = News.objects.filter(c2p__parent__id=newsCategory.id).exclude(id=new.id)[:3]
        similar_news_ids = [sim_news.pk for sim_news in similar_news]
        similarValues = Item.getItemsAttributesValues(('NAME', 'DETAIL_TEXT', 'IMAGE', 'SLUG'), similar_news_ids)
    except ObjectDoesNotExist:
        similarValues = None
        pass



    func.addToItemDictinoryWithCountryAndOrganization(id, newValues)


    template = loader.get_template('News/detailContent.html')

    context = RequestContext(request, {'newValues': newValues, 'photos': photos, 'similarValues': similarValues})
    return template.render(context)
