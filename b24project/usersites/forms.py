# -*- coding: utf-8 -*-

import uuid
import logging

from django import forms
from django.conf import settings
from django.utils.translation import get_language, ugettext as _

from b24online.models import Profile
from usersites.models import UserSiteTemplate
from b24online.utils import handle_uploaded_file

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
        self.image_fields = []
        for item in extra_param_fields:
            name = item.get('name')
            fieldtype = item.get('fieldtype')
            label = item.get('label')
            required = item.get('required', False)
            pre_text = item.get('pre_text')
            post_text = item.get('post_text')
            read_only = item.get('read_only')
            initial_value = item.get('initial')
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

                if initial_value:
                    if isinstance(initial_value, str):
                        initial_value = initial_value.replace('\\n', "\n")
                        self.initial[name] = str(initial_value)
                    elif isinstance(initial_value, (list, tuple)):
                        _data = dict(
                            (f_lang, f_value) for (f_lang, f_value) in \
                                initial_value
                        )
                        current_language = get_language()
                        current_language = current_language[:2] \
                            if current_language else 'en'
                        if current_language in _data:
                            _value = str(_data[current_language])
                            self.initial[name] = _value.replace('\\n', '\n')

                self.valuable_fields.append(name)
                if fieldtype == 'image':
                    self.image_fields.append(name)

    def save(self, *args, **kwargs):
        uuid_key = 'extra_params__{0}' . format(
            self.cleaned_data['extra_params_uuid']
        )
        data = dict(
            [(field_name, field_value) for field_name, field_value \
                in self.cleaned_data.items()
                if field_name in self.valuable_fields])
        self.request.session[uuid_key] = data
        if self.image_fields:
            for field_name in self.image_fields:
                fpath = self.cleaned_data.get(field_name)
                if fpath:
                    logger.debug(fpath)
                    filepath = handle_uploaded_file(fpath)
                    full_path = (os.path.join(settings.MEDIA_ROOT, filepath))\
                        .replace('\\', '/')
                    utils.upload_images({'file': full_path})


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


class ProfileForm(forms.ModelForm):
    birthday = forms.DateField(input_formats=["%d/%m/%Y"])

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.birthday:
            self.initial['birthday'] = self.instance.birthday.strftime('%d/%m/%Y')

        self.fields['first_name'].widget.attrs.update({'class': 'text'})
        self.fields['middle_name'].widget.attrs.update({'class': 'text'})
        self.fields['last_name'].widget.attrs.update({'class': 'text'})
        self.fields['mobile_number'].widget.attrs.update({'class': 'text'})
        self.fields['site'].widget.attrs.update({'class': 'text'})
        self.fields['profession'].widget.attrs.update({'class': 'text'})
        self.fields['birthday'].widget.attrs.update({'class': 'date'})

    class Meta:
        model = Profile
        fields = ('country', 'first_name', 'middle_name', 'last_name', 'avatar', 'mobile_number',
                  'site', 'profession', 'sex', 'user_type')
        widgets = {
            'sex': forms.RadioSelect,
            'user_type': forms.RadioSelect
        }

