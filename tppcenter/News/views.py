from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import HttpResponseRedirect, HttpResponse
from core.models import Item
from appl import func
from django.forms.models import modelformset_factory
from tppcenter.forms import ItemForm,BasePhotoGallery
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from haystack.query import SQ, SearchQuerySet
import json
from django.core.exceptions import ObjectDoesNotExist


from core.tasks import addNewsAttrubute
from django.conf import settings

def get_news_list(request, page=1, item_id=None, my=None, slug=None):

    current_company = request.session.get('current_company', False)
    description = ""
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    scripts = []

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")
    try:
        if not item_id:
            attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG')
            newsPage = func.setContent(request, News, attr, 'news', 'News/contentPage.html', 5, page=page, my=my)

        else:
            result = _getdetailcontent(request, item_id)
            newsPage = result[0]
            description = result[1]

    except ObjectDoesNotExist:
        newsPage = func.emptyCompany()

    cabinetValues = func.getB2BcabinetValues(request)

    styles = []
    scripts = []

    if not request.is_ajax():
        user = request.user



        current_section = _("News")

        templateParams = {

            'current_section': current_section,

            'newsPage': newsPage,
            'scripts': scripts,
            'current_company': current_company,
            'styles': styles,
            'search': request.GET.get('q', ''),
            'addNew': reverse('news:add'),
            'cabinetValues': cabinetValues,
            'description': description
        }

        return render_to_response("News/index.html", templateParams, context_instance=RequestContext(request))
    else:

        serialize = {
            'styles': styles,
            'scripts': scripts,
            'content': newsPage
        }

        return HttpResponse(json.dumps(serialize))



@login_required(login_url='/login/')
def newsForm(request, action, item_id=None):

    cabinetValues = func.getB2BcabinetValues(request)

    current_company = request.session.get('current_company', False)

    if current_company:
        current_company = Organization.objects.get(pk=current_company).getAttributeValues("NAME")

    if 'Redactor' in request.user.groups.values_list('name', flat=True):
        redactor = True
    else:
        redactor = False

    current_section = _("News")

    if action == 'add':
        newsPage = addNews(request)
    else:
        newsPage = updateNew(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'newsPage': newsPage,
        'current_company':current_company,
        'current_section': current_section,
        'cabinetValues': cabinetValues,
        'redactor': redactor
    }

    return render_to_response('News/index.html', templateParams, context_instance=RequestContext(request))


def addNews(request):
    current_company = request.session.get('current_company', None)

    if current_company:
        item = Organization.objects.get(pk=current_company)
        perm_list = item.getItemInstPermList(request.user)

        if 'add_news' not in perm_list:
             return func.permissionDenied()
    else:
        perm = request.user.get_all_permissions()

        if not {'appl.add_news'}.issubset(perm):
            return func.permissionDenied()


    form = None

    categories = func.getItemsList('NewsCategories', 'NAME')
    countries = func.getItemsList("Country", 'NAME')

    if request.POST:
        user = request.user

        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {
            'NAME': request.POST.get('NAME', ""),
            'DETAIL_TEXT': request.POST.get('DETAIL_TEXT', ""),
            'YOUTUBE_CODE': request.POST.get('YOUTUBE_CODE', ""),
            'IMAGE': request.FILES.get('IMAGE', "")
        }


        form = ItemForm('News', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company,
                                   lang_code=settings.LANGUAGE_CODE)

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
             return func.permissionDenied()

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

        values = {
            'NAME': request.POST.get('NAME', ""),
            'DETAIL_TEXT': request.POST.get('DETAIL_TEXT', ""),
            'YOUTUBE_CODE': request.POST.get('YOUTUBE_CODE', ""),
            'IMAGE': request.FILES.get('IMAGE', ""),
            'IMAGE-CLEAR': request.POST.get('IMAGE-CLEAR', " ")
        }

        form = ItemForm('News', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)

            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                   lang_code=settings.LANGUAGE_CODE)

            return HttpResponseRedirect(reverse('news:main'))



    template = loader.get_template('News/addForm.html')

    templateParams = {
        'gallery': gallery,
        'photos': photos,
        'form': form,
        'choosen_category': choosen_category,
        'categories': categories,
        'countries': countries,
        'choosen_country': choosen_country,
        'create_date':create_date
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage






def _getdetailcontent(request, id):
    new = get_object_or_404(News, pk=id)
    newValues = new.getAttributeValues(*('NAME', 'DETAIL_TEXT', 'YOUTUBE_CODE', 'IMAGE'))
    description = newValues.get('DETAIL_TEXT', False)[0] if newValues.get('DETAIL_TEXT', False) else ""
    description = func.cleanFromHtml(description)
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

    return template.render(context), description
