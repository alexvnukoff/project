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
from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from django.utils.feedgenerator import Rss201rev2Feed
from django.core.cache import cache

from datetime import datetime, timedelta
from pytz import timezone
import pytz

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
            attr = ('NAME', 'IMAGE', 'DETAIL_TEXT', 'SLUG', 'ANONS')
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



    current_section = _("News")

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
        'cabinetValues': cabinetValues,

    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def addNews(request):
    if 'Redactor' in request.user.groups.values_list('name', flat=True):
        redactor = True
    else:
        redactor = False

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
            'ANONS': request.POST.get('ANONS', ""),
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

    context = RequestContext(request, {'form': form, 'categories': categories, 'countries': countries, 'redactor': redactor})

    newsPage = template.render(context)


    return newsPage


def updateNew(request, item_id):
    if 'Redactor' in request.user.groups.values_list('name', flat=True):
        redactor = True
    else:
        redactor = False

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
            'ANONS': request.POST.get('ANONS', ""),
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
        'create_date':create_date,
        'redactor': redactor
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage






def _getdetailcontent(request, id):

    cache_name = "detail_%s" % id
    description_cache_name = "description_%s" % id
    query = request.GET.urlencode()
    cached = cache.get(cache_name)
    if not cached:
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
        rendered = template.render(context)
        cache.set(cache_name, rendered, 60*60*24*7)
        cache.set(description_cache_name, description, 60*60*24*7)

    else:
        rendered = cache.get(cache_name)
        description = cache.get(description_cache_name)

    return rendered, description






class CustomFeedGenerator(Rss201rev2Feed):
    def rss_attributes(self):
        super(CustomFeedGenerator, self).rss_attributes()
        return {"version": self._version,
                'xmlns:media': "http://search.yahoo.com/mrss/",
                "xmlns:yandex": "http://news.yandex.ru"}


    def add_root_elements(self, handler):
        handler.addQuickElement("title", self.feed['title'])
        handler.addQuickElement("link", self.feed['link'])
        handler.addQuickElement("description", self.feed['description'])
        handler.startElement('image', {})
        handler.addQuickElement("url", 'http://tppcenter.com/static/tppcenter/img/logo.png')
        handler.addQuickElement("title", "ТПП-Центер новости")
        handler.addQuickElement("link", 'http://www.tppcenter.com')
        handler.endElement('image')


        return False




    def add_item_elements(self, handler, item):
            super(CustomFeedGenerator, self).add_item_elements(handler, item)
            # Добавление кастомного тега в RSS-ленту
            handler.addQuickElement("yandex:full-text", item["content"])
            if item.get('video_url', False):
                handler.addQuickElement("enclosure", "", {'type': "video/x-ms-asf",'url':'http://tppcenter.com' +  item['video_url']})
            if item.get('image'):

                handler.addQuickElement("enclosure", "", {'type': "image/png", 'url':item['image']})







class NewsFeed(Feed):
    title = "Информационный отдел ТПП Центра"
    link = "/"
    description = "Новостная лента ТПП-Центра."
    feed_url = None

    unique_id_is_permalink = None

    feed_type = CustomFeedGenerator


    def items(self):
        group = Group.objects.get(name='Redactor')
        users = group.user_set.all()
        return News.active.get_active().filter(create_user__in=users)[:20]


    def item_title(self, item):
        return item.getName()


    def item_description(self, item):
        pass

    def item_guid(self, obj):
        pass


    def item_link(self, item):
        slug = item.getAttributeValues('SLUG')[0]
        return reverse('news:detail', args=[slug])


    def item_pubdate(self, item):
        moscow = timezone("Europe/Moscow")
        utc = pytz.utc

        utc_dt = utc.localize(datetime.utcfromtimestamp(item.create_date.timestamp()))

        mos_dt = utc_dt.astimezone(moscow)
        return mos_dt

    def item_extra_kwargs(self, item):
        video_url = reverse('news:detail', args=[item.getAttributeValues('SLUG')[0]]) if item.getAttributeValues('YOUTUBE_CODE') else False
        image = (settings.MEDIA_URL + 'big/' + item.getAttributeValues('IMAGE')[0]) if item.getAttributeValues('IMAGE') else False

        return {"content": item.getAttributeValues('DETAIL_TEXT')[0], 'video_url': video_url, 'image': image}






