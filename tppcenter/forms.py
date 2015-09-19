import os
from django import forms
from django.core.exceptions import ValidationError
from b24online.models import GalleryImage, Document


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
