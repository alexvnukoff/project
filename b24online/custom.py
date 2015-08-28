from urllib.parse import urljoin

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.encoding import filepath_to_uri


class CustomImageField(models.ImageField):
    def _get_url_by_size(self):
        self._require_file()
        return self.storage.url_by_size(self.name)
    url_by_size = property(_get_url_by_size)


class S3FileStorage(FileSystemStorage):
    pass


class S3ImageStorage(S3FileStorage):

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        filepath = "/original/%s" % name
        return urljoin(self.base_url, filepath_to_uri(filepath))

    def url_by_size(self, name):
        return self.ImageDimension(name)


class ImageDimension:
    def __init__(self, filepath):
        self.filepath = filepath

    def __getattr__(self, item):
        return "%s/%s" % (str(item), self.filepath)

    def __str__(self):
        return "original/%s" % self.filepath