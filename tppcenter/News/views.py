from datetime import datetime

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext as _, trans_real
from django.utils.timezone import now
from pytz import timezone
import pytz
from django.conf import settings

from appl import func
from appl.models import Organization, Gallery, Country, NewsCategories
from b24online.cbv import ItemsList, ItemDetail
from b24online.models import News
from core.models import Group
from tppcenter.forms import ItemForm, BasePhotoGallery
from core.tasks import addNewsAttrubute


class NewsList(ItemsList):
    # pagination url
    url_paginator = "news:paginator"
    url_my_paginator = "news:my_main_paginator"
    addUrl = 'news:add'

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'tppcenter/css/news.css',
        settings.STATIC_URL + 'tppcenter/css/company.css'
    ]

    current_section = _("News")
    project_news = False

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company']

    model = News

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'News/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'News/index.html'

    def _is_redactor(self):
        if 'Redactor' in self.request.user.groups.values_list('name', flat=True):
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super(NewsList, self).get_context_data(**kwargs)

        context['redactor'] = False

        if self.request.user.is_authenticated():
            context['redactor'] = self._is_redactor()

        return context

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization', 'organization__countries')

    def filter_search_object(self, s):
        return super().filter_search_object(s).query('match', is_tv=False)

    def get_queryset(self):
        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = self.model.objects.filter(organization_id=current_org)
            else:
                queryset = self.model.objects.filter(created_by=self.request.user, organization__isnull=True)
        elif self.is_filtered():
            return super().get_queryset()
        else:
            queryset = super().get_queryset().filter(is_tv=False)

            if self.project_news:
                #TODO
                pass

        return queryset


class NewsDetail(ItemDetail):
    model = News
    template_name = 'News/detailContent.html'

    current_section = _("News")
    addUrl = 'news:add'

    def get_queryset(self):
        return super().get_queryset().filter(is_tv=False).prefetch_related('galleries', 'galleries__gallery_items')

    def _get_similar_news(self):
        return News.objects.filter(is_tv=False, categories__in=self.object.categories.all())[:4]

    def get_context_data(self, **kwargs):
        context = super(NewsDetail, self).get_context_data(**kwargs)
        context['similarNews'] = self._get_similar_news()

        return context


@login_required(login_url='/login/')
def news_form(request, action, item_id=None):
    if item_id:
        if not News.active.get_active().filter(pk=item_id).exists():
            return HttpResponseNotFound()

    newsPage = ''
    current_section = _("News")

    if action == 'delete':
        newsPage = delete_news(request, item_id)
    elif action == 'add':
        newsPage = add_news(request)
    elif action == 'update':
        newsPage = update_news(request, item_id)

    if isinstance(newsPage, HttpResponseRedirect) or isinstance(newsPage, HttpResponse):
        return newsPage

    templateParams = {
        'formContent': newsPage,
        'current_section': current_section,
    }

    return render_to_response('forms.html', templateParams, context_instance=RequestContext(request))


def add_news(request):
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
        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('News', values=values)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)
            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, current_company=current_company,
                                   lang_code=trans_real.get_language())

            return HttpResponseRedirect(reverse('news:main'))

    template = loader.get_template('News/addForm.html')

    context = RequestContext(request,
                             {'form': form, 'categories': categories, 'countries': countries, 'redactor': redactor})

    newsPage = template.render(context)

    return newsPage


def update_news(request, item_id):
    if 'Redactor' in request.user.groups.values_list('name', flat=True):
        redactor = True
    else:
        redactor = False

    try:
        item = Organization.objects.get(p2c__child=item_id)
        perm_list = item.getItemInstPermList(request.user)

        if 'change_news' not in perm_list:
            raise PermissionError('permission denied')

    except Exception:
        perm = request.user.get_all_permissions()

        if not {'appl.change_news'}.issubset(perm) or not 'Redactor' in request.user.groups.values_list('name',
                                                                                                        flat=True):
            return func.permissionDenied()

    create_date = News.objects.get(pk=item_id).create_date

    try:
        choosen_category = NewsCategories.objects.get(p2c__child=item_id)
    except ObjectDoesNotExist:
        choosen_category = ''
    try:
        choosen_country = Country.objects.get(p2c__child=item_id)
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

        values = {}
        values.update(request.POST)
        values.update(request.FILES)
        form = ItemForm('News', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and form.is_valid():
            func.notify("item_creating", 'notification', user=request.user)

            addNewsAttrubute.delay(request.POST, request.FILES, user, settings.SITE_ID, item_id=item_id,
                                   lang_code=trans_real.get_language())

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
        'create_date': create_date,
        'redactor': redactor
    }

    context = RequestContext(request, templateParams)
    newsPage = template.render(context)

    return newsPage


def delete_news(request, item_id):
    if not 'Redactor' in request.user.groups.values_list('name', flat=True):

        item = Organization.objects.get(p2c__child=item_id)

        perm_list = item.getItemInstPermList(request.user)

        if 'delete_news' not in perm_list:
            return func.permissionDenied()

    instance = News.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()
    instance.reindexItem()

    return HttpResponseRedirect(request.GET.get('next'), reverse('proposal:main'))


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
            handler.addQuickElement("enclosure", "",
                                    {'type': "video/x-ms-asf", 'url': 'http://tppcenter.com' + item['video_url']})
        if item.get('image'):
            handler.addQuickElement("enclosure", "", {'type': "image/png", 'url': item['image']})


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
        return News.active.get_active() \
                   .filter(create_user__in=users, c2p__parent__in=NewsCategories.objects.all()) \
                   .order_by("-create_date")[:20]

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
        video_url = reverse('news:detail', args=[item.getAttributeValues('SLUG')[0]]) if item.getAttributeValues(
            'YOUTUBE_CODE') else False
        image = (settings.MEDIA_URL + 'original/' + item.getAttributeValues('IMAGE')[0]) if item.getAttributeValues(
            'IMAGE') else False

        return {"content": item.getAttributeValues('DETAIL_TEXT')[0], 'video_url': video_url, 'image': image}
