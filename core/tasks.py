from __future__ import absolute_import
from core.models import Item
from celery import shared_task
from appl import func
from PIL import Image
from django.conf import settings
import tinys3
from time import sleep

@shared_task
def add(pk, user, attrs=None, imageFile=None):

    sizes = {
        'big': {'box': (500, 500), 'fit': False},
        'small': {'box': (200, 200), 'fit': False},
        'th': {'box':(80, 80), 'fit': True}
    }

    if attrs is None:
        attrs = {}


    if imageFile:
        try:
            itm = Item.objects.get(pk=pk)

            im = Image.open(imageFile)
            requests = []

            sleep(600)

            for type, size in sizes.items():
                path = '/' + type + '/01/02/03/a.jpg'
                out = settings.MEDIA_ROOT + '/' + type + '-a.jpg'
                func.resize(im, out=out, **size)

                f = open(out, 'rb')

                # Creating a simple connection
                pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                         endpoint='s3.amazonaws.com')

                # Uploading a single file
                #f = open('some_file.zip','rb')
                requests.append(pool.upload(path, f))

            f = open(imageFile, 'rb')

            requests.append(pool.upload('/01/02/03/a.jpg', f))
            pool.all_completed(requests)

            attrs['IMAGE'] = '/01/02/03/a.jpg'
            itm.setAttributeValue(attrs, user)
        except Exception as e:
            raise e
            return False


    return True
