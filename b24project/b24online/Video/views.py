# -*- encoding: utf-8 -*-
from datetime import datetime
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.conf import settings
from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate
from b24online.models import Video, Organization


class VideoList(ItemsList):
    # pagination url
    url_paginator = "video:paginator"
    url_my_paginator = "video:my_main_paginator"
    addUrl = 'video:add'

    project_news = False

    sortFields = {
        'date': 'created_at',
        'name': 'title'
    }

    # allowed filter list
    # filter_list = ['tpp', 'country', 'company']

    @property
    def current_section(self):
        return _("Video")

    model = Video

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Video/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Video/index.html'

    def _is_redactor(self):
        if 'Redactor' in self.request.user.groups.values_list('name', flat=True):
            return True

        return False

    def get_context_data(self, **kwargs):
        context = super(VideoList, self).get_context_data(**kwargs)

        context['redactor'] = False

        if self.request.user.is_authenticated():
            context['redactor'] = self._is_redactor()

        return context

    def optimize_queryset(self, queryset):
        return queryset.select_related('country').prefetch_related('organization', 'organization__countries')

    def filter_search_object(self, s):
        return super().filter_search_object(s)

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
            queryset = super().get_queryset()

        return queryset


class VideoDetail(ItemDetail):
    model = Video
    template_name = 'b24online/Video/detailContent.html'

    current_section = _("Video")
    addUrl = 'video:add'

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super(VideoDetail, self).get_context_data(**kwargs)

        return context


class DeleteVideo(ItemDeactivate):
    model = Video


class VideoCreate(ItemCreate):
    model = Video
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'b24online/Video/addForm.html'
    success_url = reverse_lazy('video:my_main')
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


class VideoUpdate(ItemUpdate):
    model = Video
    fields = ['title', 'image', 'content', 'keywords', 'short_description', 'video_code']
    template_name = 'b24online/Video/addForm.html'
    success_url = reverse_lazy('video:main')

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

