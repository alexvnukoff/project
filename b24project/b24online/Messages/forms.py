# -*- encoding: utf-8 -*-

from django import forms

from b24online.models import Message


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('subject', 'content')
