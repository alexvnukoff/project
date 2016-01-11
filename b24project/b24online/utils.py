# -*- encoding: utf-8 -*-

import importlib
import os
import uuid
import socket
import logging
from PIL import Image

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File, locks
from django.core.files.move import file_move_safe
from django.utils import translation
from django.utils.text import slugify
from django.utils.timezone import now

import errno
from unidecode import unidecode

logger = logging.getLogger(__name__)

def get_index_name(lang=None, index_prefix='b24-'):
    if lang:
        return '%s%s' % (index_prefix, lang)

    if translation.get_language():
        return '%s%s' % (index_prefix, translation.get_language()[0:2])

    return '%s%s' % (index_prefix, settings.MODELTRANSLATION_DEFAULT_LANGUAGE)


def deep_merge_dict(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deep_merge_dict(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]

    return a


def reindex_instance(instance):
    from b24online.search_indexes import SearchEngine
    conn = SearchEngine.get_connection()
    languages = [lan[0] for lan in settings.LANGUAGES]

    for lang in languages:
        search_results = SearchEngine(lang=lang, doc_type=instance.get_index_model()) \
            .query('match', django_id=instance.pk).execute().hits
        index_representation = instance.get_index_model().to_index(instance)

        if search_results.total > 0:
            search_results[0].update(**index_representation.to_dict())
        else:
            index_name = get_index_name(lang)
            index_representation.save(using=conn, index=index_name)


def create_slug(string):
    """
        Creating url slug from some string using unicode to acii decoder( unidecode library)

        str string - unicode string to convert to slug
        int pk - item pk to append to the slug
    """
    # TODO: Create map for each lang
    string = unidecode(string)

    return slugify(string)


def generate_upload_path(instance, filename):
    name = str(uuid.uuid4())
    i = now()
    folder = "%s/%s/%s" % (i.year, i.month, i.day)
    ext = os.path.splitext(filename)[1]

    return '%s/%s%s' % (folder, name, ext)


def document_upload_path(instance, filename):
    return "document/%s" % generate_upload_path(instance, filename)


def resize(img, box, fit, out):
    """
    Downsample the image.
        @param img: Image -  an Image-object
        @param box: tuple(x, y) - the bounding box of the result image
        @param fit: boolean - crop the image to fill the box
        @param out: file-like-object - save the image into the output stream
        """
    # pre resize image with factor 2, 4, 8 and fast algorithm

    img = Image.open(img)

    factor = 1
    while img.size[0] / factor > 2 * box[0] and img.size[1] / factor > 2 * box[1]:
        factor *= 2
    if factor > 1:
        img.thumbnail((img.size[0] / factor, img.size[1] / factor), Image.NEAREST)

    # calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        width_ratio = 1.0 * x2 / box[0]
        height_ratio = 1.0 * y2 / box[1]
        if height_ratio > width_ratio:
            y1 = int(y2 / 2 - box[1] * width_ratio / 2)
            y2 = int(y2 / 2 + box[1] * width_ratio / 2)
        else:
            x1 = int(x2 / 2 - box[0] * height_ratio / 2)
            x2 = int(x2 / 2 + box[0] * height_ratio / 2)
        img = img.crop((x1, y1, x2, y2))

    # Resize the image with best quality algorithm ANTI-ALIAS
    img.thumbnail(box, Image.ANTIALIAS)

    if img.mode == "CMYK":
        img = img.convert("RGB")

    # save it into a file-like object
    img.save(out, "PNG", quality=95)


def handle_uploaded_file(content):
    generated_path = generate_upload_path(None, content.name)
    full_path = (os.path.join(settings.MEDIA_ROOT, generated_path)).replace('\\', '/')

    if not hasattr(content, 'chunks'):
        content = File(content)

    # Create any intermediate directories that do not exist.
    # Note that there is a race between os.path.exists and os.makedirs:
    # if os.makedirs fails with EEXIST, the directory was created
    # concurrently, and we can continue normally. Refs #16082.
    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    if not os.path.isdir(directory):
        raise IOError("%s exists and is not a directory." % directory)

    # There's a potential race condition between get_available_name and
    # saving the file; it's possible that two threads might return the
    # same name, at which point all sorts of fun happens. So we need to
    # try to create the file, but if it already exists we have to go back
    # to get_available_name() and try again.

    while True:
        try:
            # This file has a file path that we can move.
            if hasattr(content, 'temporary_file_path'):
                file_move_safe(content.temporary_file_path(), full_path)

            # This is a normal uploadedfile that we can stream.
            else:
                # This fun binary flag incantation makes os.open throw an
                # OSError if the file already exists before we open it.
                flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                # The current umask value is masked out by os.open!
                fd = os.open(full_path, flags, 0o666)
                _file = None
                try:
                    locks.lock(fd, locks.LOCK_EX)
                    for chunk in content.chunks():
                        if _file is None:
                            mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                            _file = os.fdopen(fd, mode)
                        _file.write(chunk)
                finally:
                    locks.unlock(fd)
                    if _file is not None:
                        _file.close()
                    else:
                        os.close(fd)
        except OSError as e:
            if e.errno == errno.EEXIST:
                generated_path = generate_upload_path(None, content.name)
                full_path = (os.path.join(settings.MEDIA_ROOT, generated_path)).replace('\\', '/')
            else:
                raise
        else:
            # OK, the file save worked. Break out of the loop.
            break

    return generated_path


def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


class GeoIPHelper(object):
    """
    GeoIP actions wrapper.
    """
    IP_KEYS_ORDER = (
        'HTTP_X_FORWARDED_FOR',
        'HTTP_CLIENT_IP',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_VIA',
        'X_FORWARDED_FOR',
        'REMOTE_ADDR',
    )

    @staticmethod
    def is_valid_ip(ip_str):
        """
        Check the validity of an IPv4 address
        """
        try:
            socket.inet_pton(socket.AF_INET, ip_str)
        except AttributeError:
            try:
                socket.inet_aton(ip_str)
            except (AttributeError, socket.error):
                return False
            return ip_str.count('.') == 3
        except socket.error:
            return False
        return True

    @classmethod
    def get_request_ip(cls, request):
        """
        Return the real IP fetched from request META headers.
        """
        ip = None
        for key in cls.IP_KEYS_ORDER:
            value = request.META.get(key, '').strip()
            if value:
                ips = [ip.strip().lower() for ip in value.split(',')]
                for ip_str in ips:
                    if ip_str and cls.is_valid_ip(ip_str):
                        return ip_str
        return ip
    
    @classmethod
    def get_geoip_data(cls, ip):
        """
        Fetch the info from GeoIP database by IP address.
        """
        import GeoIP

        geoip_data = {}
        gi_db_path = getattr(settings, 'GEOIP_DB_PATH', None)
        if gi_db_path:
            try:
                gi_city_h = GeoIP.open(
                    os.path.join(gi_db_path, 'GeoLiteCity.dat'),
                    GeoIP.GEOIP_STANDARD)
            except GeoIP.error:
                pass
            else:
                geoip_data = gi_city_h.record_by_addr(ip) or {}
                if not geoip_data:
                    try:
                        gi_country_h = GeoIP.open(
                            os.path.join(gi_db_path, 'GeoIP.dat'),
                            GeoIP.GEOIP_STANDARD)
                    except GeoIP.error:
                        pass
                    else:
                        country_code = gi_country_h.country_code_by_addr(ip)
                        if country_code:
                            geoip_data['country_code'] = country_code
        return geoip_data
