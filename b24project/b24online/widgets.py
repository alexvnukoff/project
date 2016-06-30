# -*- encoding: utf-8 -*-

"""
Extra widgets for forms fields.
"""

import logging

from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict

logger = logging.getLogger(__name__)


class JsTreeInput(widgets.HiddenInput):
    """
    The widget for JSTree field.
    """
    def render(self, name, value, attrs=None, url=None, **kwargs):
        if attrs is None:
            attrs = {}
        attrs['class'] = 'js-tree-field'
        return super(JsTreeInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        data_values_str = data.get(name)
        if data_values_str[0] == '[':
            data_values_str = data_values_str[1:]
        if data_values_str[-1] == ']':
            data_values_str = data_values_str[:-1]
        data_values = [item.strip() for item in data_values_str.split(',')]
        return data_values

