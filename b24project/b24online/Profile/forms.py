from django import forms
from b24online.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('country', 'first_name', 'middle_name', 'last_name',
        'mobile_number', 'site', 'profession', 'sex', 'user_type', 'contacts')
        widgets = {
            'sex': forms.RadioSelect,
            'user_type': forms.RadioSelect,
            'contacts': forms.Textarea
        }

    birthday = forms.DateField(input_formats=["%d/%m/%Y"])
    facebook = forms.CharField(required=False)
    linkedin = forms.CharField(required=False)
    co = forms.CharField(required=False)
    co_slogan = forms.CharField(required=False)
    co_description = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.birthday:
            self.initial['birthday'] = self.instance.birthday.strftime('%d/%m/%Y')

        self.initial['facebook'] = self.instance.facebook
        self.initial['linkedin'] = self.instance.linkedin
        self.initial['co'] = self.instance.co
        self.initial['co_slogan'] = self.instance.co_slogan
        self.initial['co_description'] = self.instance.co_description

        self.fields['first_name'].widget.attrs.update({'class': 'text'})
        self.fields['middle_name'].widget.attrs.update({'class': 'text'})
        self.fields['last_name'].widget.attrs.update({'class': 'text'})
        self.fields['mobile_number'].widget.attrs.update({'class': 'text'})
        self.fields['site'].widget.attrs.update({'class': 'text'})
        self.fields['profession'].widget.attrs.update({'class': 'text'})
        self.fields['birthday'].widget.attrs.update({'class': 'date'})
        self.fields['contacts'].widget.attrs.update({'class': 'textarea'})
        self.fields['facebook'].widget.attrs.update({'class': 'text'})
        self.fields['linkedin'].widget.attrs.update({'class': 'text'})
        self.fields['co'].widget.attrs.update({'class': 'text'})
        self.fields['co_slogan'].widget.attrs.update({'class': 'text'})
        self.fields['co_description'].widget.attrs.update({'class': 'textarea'})


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)

