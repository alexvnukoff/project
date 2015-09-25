from django.contrib.sites.models import Site
from django.views.generic import ListView, DetailView
from appl import func


class ItemList(ListView):
    filter_key = 'organization'
    url_paginator = None
    title = None
    current_section = None

    def get_url_paginator(self):
        return self.url_paginator

    def get_title(self):
        return self.title

    def get_current_section(self):
        return self.current_section

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data.update(
            url_paginator=self.get_url_paginator(),
            paginator_range=func.get_paginator_range(context_data['page_obj']),
            title=self.get_title(),
            current_section=self.get_current_section()
        )

        return context_data

    def get_filter_key(self):
        return self.filter_key

    def get_filter_kwargs(self):
        organization = Site.objects.get_current().user_site.organization

        return {
            self.get_filter_key(): organization
        }

    def get_queryset(self):
        return self.model.active_objects.filter(**self.get_filter_kwargs())


class ItemDetail(DetailView):
    filter_key = 'organization'

    def get_filter_key(self):
        return self.filter_key

    def get_filter_kwargs(self):
        organization = Site.objects.get_current().user_site.organization

        return {
            self.get_filter_key(): organization
        }

    def get_queryset(self):
        return self.model.active_objects.filter(**self.get_filter_kwargs())
