from __future__ import absolute_import
from core.models import Item

from appl import func
from PIL import Image
from django.conf import settings
from django.utils.timezone import now
import tinys3
import uuid
import time
import os
from celery import shared_task
import logging
logger = logging.getLogger('django.request')

def add(imageFile=None, sizes=None):

    if not sizes:
        sizes = {
            'big': {'box': (500, 500), 'fit': False},
            'small': {'box': (200, 200), 'fit': False},
            'th': {'box':(80, 80), 'fit': True}
        }

    name = str(uuid.uuid4())
    i = now()
    folder = "%s/%s/%s" % (i.year, i.month, i.day)



    #time.sleep(60)

    if imageFile:
        try:

            expires = 60 * 60 * 24 * 7

            im = Image.open(imageFile)
            requests = []

            x, y = im.size
            del im

            if x > 800 or y > 800:
                func.resize(imageFile, (800, 800), False, imageFile)

            # Creating a pool connection
            pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                         endpoint='s3.amazonaws.com')
            f = {}

            for sizeType, size in sizes.items():
                path = '/' + sizeType + '/'+ folder + '/' + name + '.png'
                out = '%s-%s.%s' % (sizeType, name, 'png')
                out = os.path.join(settings.MEDIA_ROOT, 'upload', out).replace('\\', '/')
                func.resize(imageFile, out=out, box=size['box'], fit=size['fit'])

                f[sizeType] = open(out, 'rb')

                # Uploading a single file
                #f = open('some_file.zip','rb')
                requests.append(pool.upload(path, f[sizeType], close=True, expires=expires))




            f['original'] = open(imageFile, 'rb')

            requests.append(pool.upload('/original/' + folder + '/' + name + '.png', f['original'], close=True, expires=expires))

            pool.all_completed(requests)

            filename = imageFile


        except Exception as e:
            logger.exception("Error in uploading image",  exc_info=True)

            return False

        try:
            if os.path.isfile(filename):
                    os.remove(filename)


            for key in sizes.keys():
                filename = '%s-%s' % (key, name + '.png')
                filename = os.path.join(settings.MEDIA_ROOT, 'upload', filename).replace('\\', '/')

                if os.path.isfile(filename):
                   os.remove(filename)

        except Exception:
            logger.exception("Error in removing images after uploading",  exc_info=True)
            pass


    return folder + '/' + name + '.png'

def addFile(file=None):
    ext = file.split('.')[-1]
    name = "%s.%s" % (uuid.uuid4(), ext)
    i = now()
    folder = "%s/%s/%s" % (i.year, i.month, i.day)



    #time.sleep(60)

    if file:
        try:
            requests = []
            # Creating a pool connection
            pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                         endpoint='s3.amazonaws.com')

            path = '/document/' + folder + '/' + name
            f = open(file, 'rb')
            requests.append(pool.upload(path, f, close=True))
            pool.all_completed(requests)
            filename = file
            if os.path.isfile(filename):
                    os.remove(filename)
        except Exception as e:
            logger.exception("Error in uploading file",  exc_info=True)
            return False

    return folder + '/' + name


def delete(toDelete=None):
     sizes = ['big', 'small', 'th']

     pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                                                endpoint='s3.amazonaws.com')
     requests = []
     if not toDelete:
         return False
     try:
         for delete in toDelete:
            filename = delete
            requests.append(pool.delete('/original/' + filename))
         for size in sizes:
            for delete in toDelete:
                filename = size + '/' + delete
                requests.append(pool.delete(filename))

         pool.all_completed(requests)
     except Exception as e:
         logger.exception("Error in delete image method",  exc_info=True)
         return False


     return True

def deleteFile(toDelete=None):


     pool = tinys3.Pool(settings.AWS_SID, settings.AWS_SECRET, default_bucket=settings.BUCKET,
                                                                endpoint='s3.amazonaws.com')
     requests = []
     if not toDelete:
         return False
     try:
         for delete in toDelete:
            filename = delete
            requests.append(pool.delete('/document/' + filename))


         pool.all_completed(requests)
     except Exception as e:
         logger.exception("Error in deleteFile method",  exc_info=True)
         return False


     return True
