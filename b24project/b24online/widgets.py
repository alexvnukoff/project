# -*- encoding: utf-8 -*-

"""
Extra widgets for forms fields.
"""

import logging

from django.forms import widgets
from django.utils.safestring import mark_safe

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
