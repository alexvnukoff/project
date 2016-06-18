import json

from django.http import HttpResponse
from django.views.generic.list import MultipleObjectTemplateResponseMixin, BaseListView


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(self.get_data(context)), content_type="application/json")

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context

class HybridListView(JSONResponseMixin, MultipleObjectTemplateResponseMixin, BaseListView):
    without_json = False
    
    def render_to_response(self, context, **response_kwargs):
        if not self.without_json and self.request.is_ajax():
            return self.render_to_json_response(context)
        else:
            return super(HybridListView, self).render_to_response(context)
