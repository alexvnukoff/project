import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic.list import MultipleObjectTemplateResponseMixin, BaseListView


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(self.get_data(context))

    def get_data(self, context):
        return context


class HybridListView(JSONResponseMixin, MultipleObjectTemplateResponseMixin, BaseListView):
    without_json = False

    def render_to_response(self, context, **response_kwargs):
        if not self.without_json and self.request.is_ajax():
            return self.render_to_json_response(context)
        else:
            return super(HybridListView, self).render_to_response(context)
