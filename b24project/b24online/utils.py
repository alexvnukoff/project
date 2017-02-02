# -*- encoding: utf-8 -*-
import errno
import importlib
import logging
import os
import uuid

import boto3
from PIL import Image
from boto3.s3.transfer import S3Transfer
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File, locks
from django.core.files.move import file_move_safe
from django.db.models import Q
from django.utils import translation
from django.utils._os import abspathu
from django.utils.lru_cache import lru_cache
from django.utils.text import slugify
from django.utils.timezone import now
from django_s3_storage.storage import S3Storage, S3File
from mptt.models import MPTTModel
from mptt.utils import get_cached_trees
from unidecode import unidecode
from django.utils.translation import activate, deactivate
from tpp.DynamicSiteMiddleware import get_current_site

logger = logging.getLogger(__name__)

class ExtendedS3File(S3File):
    def url(self):
        return self._storage.url(str(self))

class ExtendedS3Storage(S3Storage):
    def _open(self, name, mode="rb"):
        file = super()._open(name, mode)
        file.__class__ = ExtendedS3File

        return file


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
        activate(lang)
        search_results = SearchEngine(lang=lang, doc_type=instance.get_index_model()) \
            .query('match', django_id=instance.pk).execute().hits
        index_representation = instance.get_index_model().to_index(instance)

        if search_results.total > 0:
            search_results[0].update(**index_representation.to_dict())
        else:
            index_name = get_index_name(lang)
            index_representation.save(using=conn, index=index_name)
        deactivate()


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


def document_upload_path(instance, filename, folder='document'):
    return "%s/%s" % (folder, generate_upload_path(instance, filename))


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


@lru_cache(maxsize=32)
def get_org_by_id(id):
    from b24online.models import Organization
    try:
        return Organization.objects.get(pk=id)
    except Organization.DoesNotExist:
        return None


def get_current_organization(request):
    """
    Return the current organization (stored in request.session)
    """
    current_organization_id = request.session.get('current_company')
    return get_org_by_id(current_organization_id) if current_organization_id \
        else None


def get_permitted_orgs(user, permission='b24online.manage_organization',
                       model_klass=None):
    """
    Return the queryset if permitted Organizations.
    """
    from django.db import models
    from b24online.models import Organization
    from guardian.shortcuts import get_objects_for_user

    qs = get_objects_for_user(user, [permission],
                              Organization.get_active_objects().all(), with_superuser=False)

    if model_klass and issubclass(model_klass, models.Model):
        model_content_type = ContentType.objects.get_for_model(model_klass)
        qs = qs.filter(polymorphic_ctype_id=model_content_type)
    return qs


class MTTPTreeBuilder(object):
    """
    Json tree builder fo MTTPModel subclasses.
    """

    default_attrs = ('id', 'name', 'image.small')

    def __init__(self, model_class, node_id=None,
                 attrs=(), extract_data_fn=False):
        """
        Init the Builder instance.
        
        :param model_class: MPTTModel subclass
        :keyword node_id: the ID of tree node, root node by default
        :keyword extract_data_fn: the data extractor
        """
        assert issubclass(model_class, MPTTModel), \
            'The parameter "model_class" is invalid'
        self.model_class = model_class
        if node_id:
            try:
                self.root_node = model_class.objects.get(pk=node_id)
            except ObjectDoesNotExist:
                raise 'There is no such node with id=<{0}>'.format(node_id)
        else:
            self.root_node = None
        self.attrs = attrs if attrs else type(self).default_attrs
        if extract_data_fn and callable(extract_data_fn):
            self.extract_data_fn = extract_data_fn
        else:
            self.extract_data_fn = self.default_extract_data
        self._root_children = get_cached_trees(
            model_class.objects.all()
        )

    @classmethod
    def get_composite_attr(cls, instance, attr_name):
        """
        Return the attribute value by composite key like 
        'item.image.small'.
        """
        attr_name_parts = attr_name.split('.')
        parts_len = len(attr_name_parts)
        if parts_len > 1:
            child_key = '.'.join(attr_name_parts[1:])
            cls.get_composite_attr(instance, child_key)
        elif parts_len == 1:
            return getattr(instance, attr_name_parts[0], None)
        else:
            return None

    @classmethod
    def default_extract_data(cls, node):
        data = {}
        if node:
            data.update(
                dict([(attr_name, getattr(node, attr_name, None)) \
                      for attr_name in cls.default_attrs])
            )
        return data

    def process_node(self, node=None, filter_ids=[], opened=[]):
        result = {}
        if node:
            result.update(self.extract_data_fn(node))
            child_nodes = node._cached_children
        else:
            child_nodes = self._root_children

        children = []
        for child_node in child_nodes:
            child_data = self.process_node(child_node)
            children.append(child_data)
        result['children'] = children
        return result

    def __call__(self, filter_ids=[], opened=[]):
        return self.process_node(filter_ids=filter_ids, opened=opened)


def get_template_with_base_path(template_name):
    user_site = get_current_site().user_site
    if user_site.user_template is not None:
        folder_template = user_site.user_template.folder_name
    else:  # Deprecated
        folder_template = 'usersites'
    return "%s/%s" % (folder_template, template_name)


def load_category_hierarchy(model, categories, loaded_categories=None):
    if not loaded_categories:
        loaded_categories = {}
    categories_to_load = []

    for category in categories:
        loaded_categories[category.pk] = category

        if category.parent_id and category.parent_id not in loaded_categories:
            categories_to_load.append(category.parent_id)

    if categories_to_load:
        queryset = model.objects.filter(pk__in=categories_to_load).order_by('level')
        loaded_categories = load_category_hierarchy(model, queryset, loaded_categories)

    return loaded_categories


def get_by_content_type(content_type_id, instance_id):
    """
    Return the instance by content_type_id and id.
    """
    try:
        content_type = ContentType.objects.get(pk=content_type_id)
    except ContentType.DoesNotExist:
        pass
    else:
        model_class = content_type.model_class()
        try:
            return model_class.objects.get(pk=instance_id)
        except model_class.DoesNotExist:
            pass
    return None


def upload_to_S3(*files):
    client = boto3.client('s3', settings.BUCKET_REGION,
                          aws_access_key_id=settings.AWS_SID,
                          aws_secret_access_key=settings.AWS_SECRET)

    transfer = S3Transfer(client)
    for file in files:
        extra_args = {'ACL': 'public-read'}
        content_type = file.get('content_type', None)

        if content_type:
            extra_args.update({'ContentType': content_type})

        transfer.upload_file(file['file'], settings.BUCKET, file['bucket_path'], extra_args=extra_args)
        os.remove(file['file'])


def upload_images(*args, base_bucket_path=""):
    images_to_upload = []

    for image in args:
        abs_path = abspathu(settings.MEDIA_ROOT)
        bucket_path = abspathu(image['file'])

        if abs_path in bucket_path:
            bucket_path = bucket_path[len(abs_path):]

        bucket_path = bucket_path.replace('\\', '/')

        filename = os.path.basename(image['file'])
        filepath = os.path.dirname(image['file'])
        try:
            image_descriptor = Image.open(image['file'])
        except IOError:
            continue
        content_type = Image.MIME.get(image_descriptor.format) or 'image/png'

        del image_descriptor

        if 'sizes' in image:
            for size_name, size_data in image['sizes'].items():
                resize_name = "%s_%s" % (size_name, filename)
                out = (os.path.join(filepath, resize_name)).replace('\\', '/')
                resize(image['file'], out=out, **size_data)

                images_to_upload.append({
                    'file': out,
                    'bucket_path': "%s%s%s" % (base_bucket_path, size_name, bucket_path),
                    'content_type': content_type,
                })

        images_to_upload.append({
            'file': image['file'],
            'bucket_path': "%soriginal%s" % (base_bucket_path, bucket_path),
            'content_type': content_type
        })

    upload_to_S3(*images_to_upload)

    return [image['bucket_path'] for image in images_to_upload]


def get_company_questionnaire_qs(organization):
    """
    Return the qs for Company's questionnaires.
    """
    from b24online.models import B2BProduct, Questionnaire, Company
    from centerpokupok.models import B2CProduct

    if isinstance(organization, Company):
        b2b_content_type, b2c_content_type = map(
            lambda model_class: ContentType.objects.get_for_model(model_class),
            (B2BProduct, B2CProduct))
        b2b_ids, b2c_ids = map(
            lambda model_class: \
                [item.id for item in model_class.get_active_objects() \
                    .filter(company=organization)],
            (B2BProduct, B2CProduct))
        return Questionnaire.get_active_objects().filter(
            (Q(content_type=b2b_content_type) & Q(object_id__in=b2b_ids)) | \
            (Q(content_type=b2c_content_type) & Q(object_id__in=b2c_ids))
        )
    else:
        return Questionnaire.objects.none()


def find_keywords(tosearch):
    """
        Automatically find seo keyword on each text using python libraries
        str to search - Text to find keywords
    """

    import string
    import difflib

    exclude = set(string.punctuation)
    exclude.remove('-')
    tosearch = ''.join(ch for ch in tosearch if ch not in exclude and (ch.strip() != '' or ch == ' '))
    words = [word.lower() for word in tosearch.split(" ") if 3 <= len(word) <= 20 and word.isdigit() is False][:30]

    length = len(words)
    keywords = []

    for word in words:
        if len(difflib.get_close_matches(word, keywords)) > 0:
            continue

        count = len(difflib.get_close_matches(word, words))

        precent = (count * length) / 100

        if 2.5 <= precent <= 3:
            keywords.append(word)

        if len(keywords) > 5:
            break

    if len(keywords) < 3:
        for word in words:
            if len(difflib.get_close_matches(word, keywords)) == 0:
                keywords.append(word)

                if len(keywords) == 3:
                    break

    return ' '.join(keywords)
