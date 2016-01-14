# -*- encoding: utf-8 -*-

import datetime

from django import forms
from django.utils.translation import gettext as _
from b24online.models import RegisteredEvent


class RegisteredEventStatsForm(forms.Form):
    """
    Form for registered events stats filter.
    """
    start_date = forms.DateField(label=_('From'),
        required=False)
    end_date = forms.DateField(label=_('To'),
        required=False)

    def __init__(self, *args, **kwargs):
        """
        Set the initial values.
        """
        super(RegisteredEventStatsForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'class': 'date'})
        self.fields['end_date'].widget.attrs.update({'class': 'date'})
        self.today = datetime.date.today()
        weekday = self.today.weekday()
        self.initial['start_date'] = self.today - datetime.timedelta(days=weekday)
        self.initial['end_date'] = \
            self.today + datetime.timedelta(days=(6 - weekday))
        
    def filter(self, qs):
        """
        Filter the queryset by dates.
        """
        data = self.cleaned_data
        return qs.filter(
            registered_at__range=(data['start_date'], data['end_date']))

    def date_range(self):
        """
        Get the dates range of the form.
        """
        start_date = end_date = None
        if hasattr(self, 'cleaned_data'):
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')        
        if not start_date:
            start_date = self.initial['start_date']        
        if not end_date:
            end_date = self.initial['end_date']        
                        
        day_count = (end_date - start_date).days + 1
        for n in range(day_count):
            _date = start_date + datetime.timedelta(days=n)
            yield (_date, True if _date == self.today else False)
