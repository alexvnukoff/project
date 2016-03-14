# -*- encoding: utf-8 -*-

import logging

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from b24online.models import (Questionnaire, Question, Answer)


class QuestionnaireForm(forms.ModelForm):

    class Meta:
        model = Questionnaire
        fields = ['content_type', 'object_id', 'name', 'short_description', 
                  'description', 'image']

    def __init__(self, request, content_type_id=None, instance_id=None, 
                 *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.request = request
        self._object = None
        self._content_type = None
        if content_type_id:
            try:
                self._content_type = ContentType.objects.get(
                    pk=content_type_id
                )
            except ContentType.DoesNotExist:
                pass
            else:
                self.fields = ['object_id', 'name', 'short_description', 
                  'description', 'image']
                model_class = self._content_type.model_class()
                if instance_id:
                    try:
                        self._object = model_class.objects.get(pk=instance_id)
                    except model_class.DoesNotExist:
                        pass
                    else:
                        self.fields = ['name', 'short_description', 
                          'description', 'image']
        
                        