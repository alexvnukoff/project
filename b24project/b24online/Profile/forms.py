from django import forms

from b24online.models import Profile


class ProfileForm(forms.ModelForm):
    birthday = forms.DateField(input_formats=["%d/%m/%Y"])

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)

        if self.instance.pk:
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

