from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from appl.models import Organization

__author__ = 'user'

class SetCurCompany:

    def process_request(self, request):
        compID = request.GET.get('set', 0)

        try:
            compID = int(compID)
        except ValueError:
            compID = 0

        if compID and request.user.is_authenticated():

            current_company = request.session.get('current_company', False)

            if compID == 0:
                request.session['current_company'] = False
            elif compID != current_company:

                try:
                    item = Organization.objects.get(pk=compID)
                except ObjectDoesNotExist:
                    return HttpResponseRedirect(reverse('denied'))

                perm_list = item.getItemInstPermList(request.user)

                if 'change_company' not in perm_list and 'change_tpp' not in perm_list:
                    return HttpResponseRedirect(reverse('denied'))

                request.session['current_company'] = compID