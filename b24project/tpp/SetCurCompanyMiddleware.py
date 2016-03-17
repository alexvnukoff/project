from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from b24online.models import Organization
from b24online.utils import get_org_by_id

'''
    Set current company in B2B for user when company selected for manging
'''


class SetCurCompany:
    def process_request(self, request):
        organization_id = request.GET.get('set', None)

        if organization_id is not None:
            try:
                organization_id = int(organization_id)
            except ValueError:
                organization_id = None

            current_company = request.session.get('current_company', None)

            if request.user and request.user.is_authenticated() and not request.user.is_anonymous():
                if organization_id is None or organization_id == 0:
                    if current_company is not None:
                        del request.session['current_company']
                elif organization_id != current_company:
                    try:
                        organization = Organization.objects.get(pk=organization_id)
                    except ObjectDoesNotExist:
                        return HttpResponseRedirect(reverse('denied'))

                    if not organization.has_perm(request.user):
                        return HttpResponseRedirect(reverse('denied'))
                    get_org_by_id.cache_clear()
                    request.session['current_company'] = organization_id
