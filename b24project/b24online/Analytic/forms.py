# -*- encoding: utf-8 -*-

import datetime
import logging

from django import forms
from django.utils.translation import gettext as _
from django.utils import timezone
from b24online.models import RegisteredEvent

logger = logging.getLogger(__name__)


class SelectPeriodForm(forms.Form):
    """
    Form for registered events stats filter.
    """
    start_date = forms.DateField(label=_('From'),
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(format = '%d/%m/%Y'),
        required=False)
    end_date = forms.DateField(label=_('To'),
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(format = '%d/%m/%Y'),
        required=False)

    def __init__(self, *args, **kwargs):
        """
        Set the initial values.
        """
        is_clear = kwargs.pop('is_clear', False)
        super(SelectPeriodForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget.attrs.update({'class': 'date'})
        self.fields['end_date'].widget.attrs.update({'class': 'date'})
        self.today = datetime.date.today()
        if not is_clear:
            weekday = self.today.weekday()
            self.initial['start_date'] = \
                self.today - datetime.timedelta(days=weekday)
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

    def date_limits(self):
        """
        Return the dict with selected period's start_date and end_date.
        """
        start_date = end_date = None
        if hasattr(self, 'cleaned_data'):
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')        
        if not start_date:
            start_date = self.initial['start_date']        
        if not end_date:
            end_date = self.initial['end_date']        

        return {
            'start_date': start_date,
            'end_date': end_date
        }

    def get_week(self, multiplier):
        """
        Return the start- and end date for some week.
        """
        date_limits = self.date_limits()
        delta = multiplier * datetime.timedelta(days=7) 
        return {
            'start_date': date_limits['start_date'] + delta,
            'end_date': date_limits['end_date'] + delta,
        }

    def next_week(self):
        """Return the next week."""
        result = self.get_week(1)
        return result if result['start_date'] <= self.today \
            else {'start_date': None, 'end_date': None}

    def prev_week(self):
        """Return the previous week."""
        return self.get_week(-1)
