
from appl.models import *

from django.forms.models import modelformset_factory

from tppcenter.forms import ItemForm, Test, BasePhotoGallery

from celery import shared_task, task

from appl import func


@shared_task
def addNewsAttrubute(post, files, user, site_id, item_id=None):
    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=3, fields=("photo",))
    gallery = Photo(post, files)

    values = {}
    values['NAME'] = post.get('NAME', "")
    values['DETAIL_TEXT'] = post.get('DETAIL_TEXT', "")
    values['IMAGE'] = files.get('IMAGE', "")

    form = ItemForm('News', values=values, id=item_id)
    form.clean()

    if gallery.is_valid() and form.is_valid():
        new = form.save(user, site_id)
        gallery.save(parent=new.id, user=user)
        func.notify("item_created", 'notification', user=user)


    return True
