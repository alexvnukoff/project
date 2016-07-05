import os
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from b24online import utils
from b24online.models import GalleryImage, Document
from b24online.utils import handle_uploaded_file


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ('image',)


class DocumentForm(forms.ModelForm):
    def clean_document(self):
        document = self.cleaned_data.get('document')

        if not document:
            return None

        ext = os.path.splitext(document.name)[1]
        valid_extensions = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.xsl']

        if ext not in valid_extensions:
            raise ValidationError('File not supported!')

        return document

    class Meta:
        model = Document
        fields = ('document',)


class EditorImageUploadForm(forms.Form):
    file = forms.ImageField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get("file")

        if image_file.size > 500 * 1024:
            self.add_error('file', _("Image file is too large"))

        if image_file and (image_file.image.width > 800 or image_file.image.height > 800):
            self.add_error('file', "The maximum size of the image is 800 x 800")

        return cleaned_data

    def save(self):
        if self.errors:
            raise ValueError("Form is not validated")

        filepath = handle_uploaded_file(self.cleaned_data['file'])
        full_path = (os.path.join(settings.MEDIA_ROOT, filepath)).replace('\\', '/')

        return utils.upload_images({'file': full_path}, base_bucket_path="editor_uploads/images/")[0]


class FeedbackForm(forms.Form):
    co_id = forms.CharField(max_length=11)
    co_email = forms.CharField(max_length=100)
    url_path = forms.CharField(max_length=225)
    realname = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(max_length=1000)

