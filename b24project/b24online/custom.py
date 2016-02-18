# -*- encoding: utf-8 -*-

import os

from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.fields.files import ImageFieldFile

from b24online.utils import resize

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


class LocalFileStorage(FileSystemStorage):
    """
    Local storage for debugging.
    """
    SIZES = {
        'big': 150,
        'th': 30,
        'small': 24,
        'middle': 70,
    }

    def url(self, name):
        return self.url_by_size(name, 'original')

    def url_by_size(self, name, size):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        size_px = type(self).SIZES.get(size)
        if size_px:
            sized_image_path = os.path.join(settings.MEDIA_ROOT, str(size), name)
            image_path = os.path.join(settings.MEDIA_ROOT, name)
            if not os.path.exists(sized_image_path) and \
                os.path.exists(image_path):

                directory = os.path.dirname(sized_image_path)
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                resize(image_path, (size_px, size_px), True, sized_image_path) 
            path = "%s/%s" % (str(size), name)
        else:
            path = name
        return urljoin(self.base_url, path)


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
