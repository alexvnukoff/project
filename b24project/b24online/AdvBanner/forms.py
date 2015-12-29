from django import forms
from django.utils.translation import gettext as _
from b24online.models import Banner, Branch, Chamber, Country


class BannerForm(forms.ModelForm):
    start_date = forms.DateField(input_formats=["%d/%m/%Y"], required=True)
    end_date = forms.DateField(input_formats=["%d/%m/%Y"], required=True)
    branches = forms.ModelMultipleChoiceField(queryset=Branch.objects.all(), required=False)
    chamber = forms.ModelMultipleChoiceField(queryset=Chamber.objects.all(), required=False)
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop("block")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date", None)
        end_date = cleaned_data.get("end_date", None)
        branches = cleaned_data.get("branches", None)
        chambers = cleaned_data.get("chamber", None)
        countries = cleaned_data.get("country", None)
        image = self.cleaned_data.get('image', None)

        if image and image.size > 200 * 1024:
            self.add_error('image', "Image file too large")

        if image and (image.image.width != self.block.width or image.image.height != self.block.height):
            self.add_error('image', "Required dimensions are: %s x %s" % (self.block.width, self.block.height))

        if start_date and end_date and start_date >= end_date:
            self.add_error('start_date', _('Starting date should be earlier than ending date'))

        if not branches and not chambers and not countries:
            raise forms.ValidationError(_('At least one filter should be specified'))

    class Meta:
        model = Banner
        fields = ['title', 'image', 'link']
