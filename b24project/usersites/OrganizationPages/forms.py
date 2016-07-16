from django import forms


class ContactForm(forms.Form):
    co_id = forms.CharField(max_length=11)
    url_path = forms.CharField(max_length=225)
    name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    message = forms.CharField(required=False)
