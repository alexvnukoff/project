from __future__ import absolute_import
from core.models import Item
from celery import shared_task
from appl import func
from PIL import Image
from django.conf import settings
from django.utils.timezone import now
import tinys3
import uuid
import time


@shared_task
def add(pk, user, attrs=None, imageFile=None):

    sizes = {
        'big': {'box': (500, 500), 'fit': False},
        'small': {'box': (200, 200), 'fit': False},
        'th': {'box':(80, 80), 'fit': True}
    }

    name = str(uuid.uuid4())
    i = now()
    folder = "%s/%s/%s" % (i.day, i.month, i.year)

    if attrs is None:
        attrs = {}

    time.sleep(60)

    if imageFile:
        try:
            itm = Item.objects.get(pk=pk)

            im = Image.open(imageFile)
            requests = []

            # Creating a pool connection
            pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                         endpoint='s3.amazonaws.com')

            for type, size in sizes.items():
                path = '/' + type + '/'+ folder + '/' + name + '.jpg'
                out = settings.MEDIA_ROOT + '/' + type + '-' + name + '.jpg'
                func.resize(im, out=out, **size)

                f = open(out, 'rb')

                # Uploading a single file
                #f = open('some_file.zip','rb')
                requests.append(pool.upload(path, f))

            f = open(imageFile, 'rb')

            requests.append(pool.upload(folder + '/' + name + '.jpg', f))
            pool.all_completed(requests)

            attrs['IMAGE'] = folder + '/' + name + '.jpg'
            itm.setAttributeValue(attrs, user)
        except Exception:
            return False


    return True
