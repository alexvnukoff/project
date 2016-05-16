# -*- coding: utf-8 -*-
import logging

from django import forms
from usersites.models import UserSiteTemplate

logger = logging.getLogger(__name__)

INTEGER, FLOAT, DATE, CHAR, TEXTAREA, BOOLEAN, IMAGE = \
    'integer', 'float', 'date', 'char', 'textarea', 'boolean', 'image'

FIELD_TYPES = {
    INTEGER: (forms.IntegerField, {}),
    FLOAT: (forms.FloatField, {}),
    DATE: (forms.DateTimeField, {}),
    CHAR: (forms.CharField, {}),
    TEXTAREA: (forms.CharField, {'widget': forms.Textarea}),
    BOOLEAN: (forms.BooleanField, {}),
    IMAGE: (forms.ImageField, {}),
}


class UserSiteTemplateForm(forms.ModelForm):
    class Meta:
        model = UserSiteTemplate
        fields = '__all__'


class ExtraParamsError(Exception):
    pass


class ExtraParamsForm(forms.Form):
    """
    The form for product extra paramemeters.
    """
    
    def __init__(self, instance, request, *args, **kwargs):
        self._instance = instance
        super(ExtraParamsForm, self).__init__(*args, **kwargs)
        extra_param_fields = getattr(instance, 'extra_params')
        if not extra_param_fields:
            raise ExtraParamsError(_('Invalid form description'))
        self.pre_texts = {}
        self.post_texts = {}
        for item in extra_param_fields:
            name = item.get('name')
            fieldtype = item.get('fieldtype')
            label = item.get('label')
            required = item.get('required', False)
            pre_text = item.get('pre_text')
            post_text = item.get('post_text')
            read_only = item.get('read_only')
            if all((fieldtype, name)) and fieldtype in FIELD_TYPES:
                field_cls, extra_params = FIELD_TYPES[fieldtype]
                field = field_cls(**extra_params)
                field.name = name
                field.label = label
                field.required = required
                if read_only:
                    field.read_only = read_only
                if pre_text:
                    self.pre_texts[name] = pre_text
                if post_text:
                    self.post_texts[name] = post_text
                self.fields[name] = field


def create_extra_form(instance, request):
    """
    Try to build and return the form for product extra params.
    """
    try:
        params = {}
        if request.method == 'POST':
            params.update({'data': request.POST, 'files': request.FILES})
        return ExtraParamsForm(instance, request, **params)
    except ExtraParamsError:
        return None
