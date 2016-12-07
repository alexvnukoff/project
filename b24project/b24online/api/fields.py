import datetime

import six
from django.utils.dateparse import parse_date
from rest_framework import ISO_8601
from rest_framework.fields import DateField
from rest_framework.settings import api_settings
from rest_framework.utils import humanize_datetime


class DateTimeToDateField(DateField):
    def to_internal_value(self, value):
        input_formats = getattr(self, 'input_formats', api_settings.DATE_INPUT_FORMATS)

        if isinstance(value, datetime.datetime):
            return value.date()

        if isinstance(value, datetime.date):
            return value

        for input_format in input_formats:
            if input_format.lower() == ISO_8601:
                try:
                    parsed = parse_date(value)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return parsed
            else:
                try:
                    parsed = self.datetime_parser(value, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return parsed.date()

        humanized_format = humanize_datetime.date_formats(input_formats)
        self.fail('invalid', format=humanized_format)

    def to_representation(self, value):
        if not value:
            return None

        output_format = getattr(self, 'format', api_settings.DATE_FORMAT)

        if output_format is None or isinstance(value, six.string_types):
            return value

        value = value.date()

        if output_format.lower() == ISO_8601:
            return value.isoformat()

        return value.strftime(output_format)