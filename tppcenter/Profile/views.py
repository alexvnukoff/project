from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from appl.models import *
from django.http import Http404, HttpResponseRedirect
from core.models import Value, Item, Attribute, Dictionary, AttrTemplate, Relationship
from appl import func
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.db.models import get_app, get_models
from tppcenter.forms import ItemForm, Test, BasePhotoGallery, BasePages
from django.template import RequestContext, loader
from datetime import datetime
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from tpp.SiteUrlMiddleWare import get_request
from celery import shared_task, task
from core.tasks import addNewTender
from django.conf import settings
from tppcenter.Profile.profileForms import ProfileForm
from core.amazonMethods import add, delete
from tppcenter.views import user_logout
import uuid
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def getProfileForm(request):
    user = request.user
    if user.is_authenticated():
        notification = len(Notification.objects.filter(user=request.user, read=False))
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None
    current_section = "Profile"




    profilePage = _profileContent(request)
    if isinstance(profilePage, HttpResponseRedirect):
        return profilePage








    return render_to_response("Profile/index.html", {'user_name': user_name, 'current_section': current_section,
                                                   'notification': notification, 'profilePage': profilePage},
                              context_instance=RequestContext(request))


def _profileContent(request):
    if request.method == 'POST':
        cabinet = Cabinet.objects.get(user=request.user.pk)
        image = cabinet.getAttributeValues('IMAGE')
        avatar = image[0] if len(image) > 0 else ""
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():

             if len(form.files) > 0:
                path_to_images = "upload/"

                if len(image) > 0:

                    delete(image[0])

                file = save_image(form.files['image'], path_to_images)
             else:
                file = image[0] if len(image) > 0 else ""


             cabinet.setAttributeValue({'PROFESSION': form.cleaned_data['profession'],
                                       'MOBILE_NUMBER': form.cleaned_data['mobile_number'],
                                       'BIRTHDAY': form.cleaned_data['birthday'],
                                       'PERSONAL_STATUS': int(form.cleaned_data['personal_status']),
                                       'SEX': int(form.cleaned_data['sex']),
                                       'SKYPE': form.cleaned_data['skype'],
                                       'SITE_NAME': form.cleaned_data['site_name'],
                                       'ICQ': form.cleaned_data['icq'],
                                       'USER_MIDDLE_NAME': form.cleaned_data['middle_name'],
                                       'USER_LAST_NAME': form.cleaned_data['last_name'],
                                       'USER_FIRST_NAME': form.cleaned_data['first_name'],
                                       'TELEPHONE_NUMBER': form.cleaned_data['telephone_number'],
                                       'IMAGE': file}, request.user)

             Relationship.objects.filter(parent__in=Country.objects.all(), child=cabinet).delete()
             Relationship.setRelRelationship(parent=Country.objects.get(pk=int(form.cleaned_data['country'])),
                                             child=cabinet, user=request.user)
             if form.cleaned_data['email'] != request.user.email:
                user = request.user
                user.email = form.cleaned_data['email']
                try:
                    user.save()
                    user_logout(request)
                    return HttpResponseRedirect(reverse("login"))
                except Exception:
                      form.errors.update({"email": _("This email already in use")})
             avatar = file
    else:
        cabinet = get_object_or_404(Cabinet, user=request.user)
        profile = cabinet.getAttributeValues('PROFESSION', 'MOBILE_NUMBER', 'BIRTHDAY', 'PERSONAL_STATUS', 'SEX',
                                             'SKYPE', 'SITE_NAME', 'ICQ', 'USER_MIDDLE_NAME', 'USER_FIRST_NAME',
                                             'USER_LAST_NAME', 'IMAGE', 'TELEPHONE_NUMBER')

        avatar = profile['IMAGE'][0] if profile.get('IMAGE', False) else ""
        if not profile:
            profile = {}
        try:
            country = Country.objects.get(p2c__child=cabinet).pk
        except Exception:
            country = ""
        dictSex = Dictionary.objects.get(title='SEX')
        sexSlot = profile['SEX'][0] if profile.get('SEX', False) else ""
        sex = dictSex.getSlotID(title=sexSlot) if sexSlot else ""

        dictStatus = Dictionary.objects.get(title='PERSONAL_STATUS')
        statusSlot = profile['PERSONAL_STATUS'][0] if profile.get('PERSONAL_STATUS', False) else ""
        status = dictStatus.getSlotID(title=statusSlot) if statusSlot else ""

        form = ProfileForm(initial={'profession': profile['PROFESSION'][0] if profile.get('PROFESSION', False) else "",
                                        'mobile_number': profile['MOBILE_NUMBER'][0] if profile.get('MOBILE_NUMBER', False) else "",
                                        'birthday': profile['BIRTHDAY'][0] if profile.get('BIRTHDAY', False) else "",
                                        'personal_status': status,
                                        'sex': sex,
                                        'country': country,
                                        'skype': profile['SKYPE'][0] if profile.get('SKYPE', False) else "",
                                        'icq': profile['ICQ'][0] if profile.get('ICQ', False) else "",
                                        'middle_name': profile['USER_MIDDLE_NAME'][0] if profile.get('USER_MIDDLE_NAME', False) else "",
                                        'last_name': profile['USER_LAST_NAME'][0] if profile.get('USER_LAST_NAME', False) else "",
                                        'site_name': profile['SITE_NAME'][0] if profile.get('SITE_NAME', False) else "",
                                        'first_name': profile['USER_FIRST_NAME'][0] if profile.get('USER_FIRST_NAME', False) else "",
                                        "telephone_number": profile['TELEPHONE_NUMBER'][0] if profile.get('TELEPHONE_NUMBER', False) else "",
                                        'email': request.user.email})



    template = loader.get_template('Profile/addForm.html')
    context = RequestContext(request, {"form": form, 'avatar': avatar})
    return template.render(context)

def save_image(file, path=''):
        """
        Method that save new file , and delete old file if exist
        parameters:

        path = path to file
        It's internal method of ItemForm class , to save files
        """


        filename = file._get_name()
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        fd = open('%s/%s' % (settings.MEDIA_ROOT, str(path) + str(filename)), 'wb')

        for chunk in file.chunks():
            fd.write(chunk)
        fd.close()

        file = '%s/%s' % (settings.MEDIA_ROOT, str(path) + str(filename))
        sizes = {
            'big': {'box': (150, 150), 'fit': False},
            'small': {'box': (100, 100), 'fit': False},
            'th': {'box': (80, 80), 'fit': True}
        }
        filename = add(imageFile=file, sizes=sizes)

        return filename