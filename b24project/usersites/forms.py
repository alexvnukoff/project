# -*- coding: utf-8 -*-

import uuid
import logging

from django import forms
from django.utils.translation import ugettext as _

from usersites.models import UserSiteTemplate

logger = logging.getLogger(__name__)


class UserSiteTemplateForm(forms.ModelForm):
    class Meta:
        model = UserSiteTemplate
        fields = '__all__'


##
# Simple form builder for extra parameters
##
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


class ExtraParamsError(Exception):
    """
    If some of form fields descriptions is invalid.
    """


class ExtraParamsForm(forms.Form):
    """
    The form for product extra paramemeters.
    """

    extra_params_uuid = forms.UUIDField(
        widget=forms.HiddenInput()
    )

    def __init__(self, instance, request, *args, **kwargs):
        self.instance = instance
        self.request = request
        super(ExtraParamsForm, self).__init__(*args, **kwargs)
        extra_param_fields = getattr(instance, 'extra_params')
        self.initial['extra_params_uuid'] = uuid.uuid4()
        if not extra_param_fields:
            raise ExtraParamsError(_('Invalid form description'))
        self.pre_texts = {}
        self.post_texts = {}
        self.valuable_fields = []
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
                self.valuable_fields.append(name)

    def save(self, *args, **kwargs):
        uuid_key = 'extra_params__{0}' . format(
            self.cleaned_data['extra_params_uuid']
        )
        logger.debug(uuid_key)
        data = dict(
            [(field_name, field_value) for field_name, field_value \
                in self.cleaned_data.items() 
                if field_name in self.valuable_fields])
        logger.debug(data)
        self.request.session[uuid_key] = dict(
            [(field_name, field_value) for field_name, field_value \
                in self.cleaned_data.items() 
                if field_name in self.valuable_fields])
        

def create_extra_form(instance, request):
    """
    Try to build and return the form for product extra params.
    """
    if 'uuid_hash' in request.session:
        try:
            params = {}
            if request.method == 'POST':
                params.update({'data': request.POST, 'files': request.FILES})
            return ExtraParamsForm(instance, request, **params)
        except ExtraParamsError:
            pass
    return None
