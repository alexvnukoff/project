from django.core.mail import EmailMessage
from appl.models import UserSites
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from recaptcha.client import captcha

def get_news_list(request):

   result = _get_content(request)
   contentPage = result[0]
   email = result[1]

   current_section = _("Contacts")
   title = _("Contacts")
   captcha_response = ""
   responseMessage = ''

   if request.POST.get('Send', False):
       name = request.POST.get('NAME', False)
       from_email = request.POST.get('EMAIL', False)
       message = request.POST.get('MESSAGE', False)
       if name and message and from_email and request.POST.get('recaptcha_response_field'):

            response = captcha.submit(
                request.POST.get('recaptcha_challenge_field'),
                request.POST.get('recaptcha_response_field'),
                '6LeHR_QSAAAAAN97GsJExYhVwHDnatXwJ8lclY7N',
                request.META['REMOTE_ADDR'],)


            if response.error_code.decode("utf-8") == 'success':

                 if email is None:

                        email = 'admin@tppcenter.com'
                        subject = _('This message was sent to company:')
                 else:
                        email = email[0]
                        subject = _('New message from ') + name
                 mail = EmailMessage(subject, message, from_email, [email])
                 mail.send()



                 responseMessage = _('The message was succesfuly send ')

            else:
                 responseMessage = _('Incoorect Recapcha')



       else:
           responseMessage = _('All field are required')





   templateParams = {
       'current_section': current_section,
       'contentPage': contentPage,
       'title': title,
       'responseMessage': responseMessage,
       'captcha_response': captcha_response

   }



   return render_to_response("index.html", templateParams, context_instance=RequestContext(request))





def _get_content(request):

     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization

     attr = ('NAME', 'ADDRESS', 'TELEPHONE_NUMBER', 'SLUG', 'POSITION', 'EMAIL')



     organizationValues = organization.getAttributeValues(*attr)

     email = organizationValues.get('EMAIL', None)





     templateParams = {
         'organizationValues': organizationValues,

     }


     template = loader.get_template('Contact/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered, email






















