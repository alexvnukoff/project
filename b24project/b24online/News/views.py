from datetime import datetime

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext as _
from pytz import timezone
import pytz
from django.conf import settings

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate, DeleteGalleryImage, \
    GalleryImageList
from b24online.models import News, Organization


class NewsList(ItemsList):
    # pagination url
    url_paginator = "news:paginator"
    url_my_paginator = "news:my_main_paginator"
    addUrl = 'news:add'

    # Lists of required scripts and styles for ajax request
    styles = [
        settings.STATIC_URL + 'b24online/css/news.css',
        settings.STATIC_URL + 'b24online/css/company.css'
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
        self.template_name = 'b24online/News/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/News/index.html'

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
                queryset = self.model.get_active_objects().filter(organization_id=current_org)
            else:
                queryset = self.model.get_active_objects().filter(created_by=self.request.user, organization__isnull=True)
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
    template_name = 'b24online/News/detailContent.html'

    current_section = _("News")
    addUrl = 'news:add'

    def get_queryset(self):
        return super().get_queryset().filter(is_tv=False).prefetch_related('galleries', 'galleries__gallery_items')

    def _get_similar_news(self):
        if self.object.categories.exists():
            return News.objects.filter(is_tv=False, categories__in=self.object.categories.all()) \
                .order_by('-created_at')[:3]

        return News.objects.filter(is_tv=False, categories=None).order_by('-created_at')[:3]

    def get_context_data(self, **kwargs):
        context = super(NewsDetail, self).get_context_data(**kwargs)
        context['similarNews'] = self._get_similar_news()

        return context


class DeleteNews(ItemDeactivate):
    model = News


class NewsGalleryImageList(GalleryImageList):
    owner_model = News
    namespace = 'news'


class DeleteNewsGalleryImage(DeleteGalleryImage):
    owner_model = News


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
        handler.addQuickElement("url", 'http://b24online.com/static/b24online/img/logo.png')
        handler.addQuickElement("title", "ТПП-Центер новости")
        handler.addQuickElement("link", 'http://www.b24online.com')
        handler.endElement('image')

        return False

    def add_item_elements(self, handler, item):
        super(CustomFeedGenerator, self).add_item_elements(handler, item)
        # Добавление кастомного тега в RSS-ленту
        handler.addQuickElement("yandex:full-text", item["content"])
        if item.get('video_url', False):
            handler.addQuickElement("enclosure", "",
                                    {'type': "video/x-ms-asf", 'url': 'http://b24online.com' + item['video_url']})
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
        return News.objects.none() # TODO

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


class NewsCreate(ItemCreate):
    model = News
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'b24online/News/addForm.html'
    success_url = reverse_lazy('news:main')
    org_required = False

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        organization_id = self.request.session.get('current_company', None)

        if organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
            form.instance.organization = organization
            form.instance.country = organization.country

        result = super().form_valid(form)
        self.object.reindex()

        if 'image' in form.changed_data:
            self.object.upload_images()

        return result


class NewsUpdate(ItemUpdate):
    model = News
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'b24online/News/addForm.html'
    success_url = reverse_lazy('news:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        organization_id = self.request.session.get('current_company', None)

        if organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
            form.instance.organization = organization
            form.instance.country = organization.country

        result = super().form_valid(form)

        if form.changed_data:
            self.object.reindex()

            if 'image' in form.changed_data:
                self.object.upload_images()

        return result

