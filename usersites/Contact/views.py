from appl.models import UserSites
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings

def get_news_list(request):

   contentPage = _get_content(request)

   current_section = _("Contacts")
   title = _("Contacts")

   templateParams = {
       'current_section': current_section,
       'contentPage': contentPage,
       'title': title
   }



   return render_to_response("index.html", templateParams, context_instance=RequestContext(request))





def _get_content(request):

     user_site = UserSites.objects.get(sites__id=settings.SITE_ID)
     organization = user_site.organization

     attr = ('NAME', 'ADDRESS', 'TELEPHONE_NUMBER', 'SLUG', 'POSITION')


     organizationValues = organization.getAttributeValues(*attr)





     templateParams = {
         'organizationValues': organizationValues,

     }


     template = loader.get_template('Contact/contentPage.html')
     context = RequestContext(request, templateParams)
     rendered = template.render(context)

     return rendered






















