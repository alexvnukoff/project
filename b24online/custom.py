from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.fields.files import ImageFieldFile


class CustomImageFieldFile(ImageFieldFile):

    @property
    def original(self):
        self._require_file()
        return self.storage.url_by_size(self.name, 'original')

    def __getattr__(self, item):
        if self.field.valid_sizes is not None and item in self.field.valid_sizes:
            self._require_file()
            return self.storage.url_by_size(self.name, item)

        return super().__getattr__(item)


class CustomImageField(models.ImageField):
    attr_class = CustomImageFieldFile

    def __init__(self, verbose_name=None, name=None, sizes=None, **kwargs):
        self.valid_sizes = sizes
        super().__init__(verbose_name, name, **kwargs)


class S3FileStorage(FileSystemStorage):
    pass


class S3ImageStorage(S3FileStorage):

    def url(self, name):
        return self.url_by_size(name, 'original')

    def url_by_size(self, name, size):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        path = "%s/%s" % (str(size), name)
        return urljoin(self.base_url, path)
