# -*- encoding: utf-8 -*-

import json
import logging
from urllib.parse import urljoin

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.http import (HttpResponse, HttpResponseRedirect,
                    HttpResponseBadRequest, JsonResponse, HttpResponseNotFound)
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from guardian.shortcuts import get_objects_for_user
from django.core.mail import send_mail

from b24online.cbv import ItemCreate
from b24online.forms import EditorImageUploadForm, FeedbackForm
from b24online.models import Chamber, B2BProduct, Greeting, BusinessProposal, Exhibition, Organization, Branch
from appl import func
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


@csrf_protect
def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('wall:main'))

    organizations_list = Chamber.get_active_objects().filter(org_type='international')

    product_list = B2BProduct.get_active_objects().select_related('company').prefetch_related('company__countries') \
                       .order_by('-created_at')[:3]
    service_list = BusinessProposal.get_active_objects() \
                       .prefetch_related('country', 'organization', 'organization__countries') \
                       .order_by('-created_at')[:3]
    greetings_list = Greeting.objects.all()
    exhibitions_list = Exhibition.get_active_objects().select_related('country').order_by('-created_at')[:3]

    template_params = {
        'organizationsList': organizations_list,
        'productsList': product_list,
        'serviceList': service_list,
        'greetingsList': greetings_list,
        'exhibitionsList': exhibitions_list,
    }
    # cache.set(cache_name, templateParams)
    # else:
    #    templateParams = cache.get(cache_name)

    template = loader.get_template('b24online/index.html')
    context = RequestContext(request, template_params)
    rendered = template.render(context)

    return HttpResponse(rendered)


@ensure_csrf_cookie
@login_required
def get_notification_list(request):
    if request.is_ajax():

        # Older notifications
        last = int(request.GET.get('last', 0))
        # New notifications
        first = int(request.GET.get('first', 0))
        # Disable loading of empty list
        last_line = False

        notifications = request.user.notifications

        if last != 0:
            notifications = notifications.filter(pk__lt=last).order_by("-pk")[:3]

            if len(notifications) < 3:
                last_line = True

        elif first != 0:
            notifications = notifications.filter(pk__gt=first).order_by("-pk")[:20]
        else:
            notifications = notifications.order_by("-pk")[:3]

        template = loader.get_template('b24online/main/notoficationlist.html')
        context = RequestContext(request, {'notifications': notifications, 'last_line': last_line})
        data = template.render(context)

        return HttpResponse(json.dumps({'data': data, 'count': request.user.notifications.filter(read=False).count()}))
    else:
        return HttpResponseBadRequest()


@ensure_csrf_cookie
def register_to_exhibition(request):
    if request.is_ajax() and request.POST.get('NAME', False) and request.POST.get('EMAIL', False):
        adminEmail = 'migirov@tppcenter.com'
        companyEmail = request.POST.get('SEND_EMAIL', None)

        message_name = _('%(name)s , was registered to your event %(event)s ,') % {"name": request.POST.get('NAME'),
                                                                                   "event": request.POST.get(
                                                                                       'EXEBITION', "")}
        message_company = (
            _('working in the %(company)s ') % {'company': request.POST.get('COMPANY')}) if request.POST.get('COMPANY',
                                                                                                             False) else ""
        message_position = (
            _('on the position of %(position)s . ') % {'position': request.POST.get('POSITION')}) if request.POST.get(
            'POSITION', False) else ""
        message_email = _('You can contact him at this email address %(email)s  ') % {
            "email": request.POST.get('EMAIL')}
        message = (message_name + message_company + message_position + message_email)

        send_mail(_('Registartion to event'), message, 'noreply@tppcenter.com',
                  [adminEmail], fail_silently=False)
        if companyEmail:
            send_mail(_('Registartion to event'), message, 'noreply@tppcenter.com',
                      [companyEmail], fail_silently=False)

    return HttpResponse("")


@login_required
def my_companies(request):
    result = {'content': [], 'total': 0}

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        return HttpResponse(json.dumps(result))

    if not request.user or not request.user.is_authenticated() or request.user.is_anonymous():
        return HttpResponse(json.dumps(result))

    if request.is_ajax():
        current_company = request.session.get('current_company', None)
        paginate_by = 10

        organizations = get_objects_for_user(request.user, ['b24online.manage_organization'],
                                             Organization.get_active_objects().all(), with_superuser=False)

        organizations = Organization.objects.filter(pk__in=organizations)

        if current_company is not None:
            organizations = organizations.exclude(pk=current_company)

            #if page == 1:
            #    user_name = request.user.profile.full_name or request.user.email
            #    result['content'] = [{'title': user_name, 'id': 0}]

        paginator = Paginator(organizations, paginate_by)
        result['total'] = paginator.count
        on_page = paginator.page(page)

        result['content'] += [{'title': organization.name, 'id': organization.pk}
                              for organization in on_page.object_list]
        return HttpResponse(json.dumps(result))

    return HttpResponse(json.dumps(result))


def json_filter(request):
    filter_key = request.GET.get('type', None)

    if filter_key is None:
        return HttpResponseBadRequest()

    q = request.GET.get('q', '').strip()

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        return HttpResponseBadRequest()

    if request.is_ajax():
        result = func.autocomplete_filter(filter_key, q, page)

        if result is not None:
            object_list, total = result

            items = [{'title': item.name, 'id': item.pk} for item in object_list]

            return HttpResponse(json.dumps({'content': items, 'total': total}))

    return HttpResponse(json.dumps({'content': [], 'total': 0}))


def get_live_top(request):
    filterAdv = func.get_list_adv_filter(request)

    models = func.get_tops(filterAdv)

    templateParams = {
        'MEDIA_URL': settings.MEDIA_URL,
        'models': models
    }

    return render_to_response("b24online/AdvTop/tops.html", templateParams)


def get_live_banner(request):
    filterAdv = func.get_list_adv_filter(request)

    places = request.POST.getlist('places[]', [])

    template_params = {
        'banners': [func.get_banner(place, None, filterAdv) for place in places]
    }

    return render_to_response("b24online/AdvBanner/banners_live.html", template_params)


def ping(request):
    from django.http import StreamingHttpResponse

    return StreamingHttpResponse('pong')


def get_additional_page(request):
    prefix = '-'.join((request.GET.get('prefix'), request.GET.get('num')))
    return render_to_response("b24online/additionalPage.html", {'prefix': prefix, 'num': int(request.GET.get('num'))})


def perm_denied(request):
    template = loader.get_template('b24online/permissionDen.html')
    context = RequestContext(request)

    return render_to_response("b24online/main/denied.html", {'DeniedContent': template.render(context)},
                              context_instance=RequestContext(request))


def branch_list(request):
    parent = request.GET.get('parent', None)
    bread_crumbs = None

    # TODO: paginate?
    branches = Branch.objects.filter(parent=parent)

    if parent is not None:
        bread_crumbs = Branch.objects.get(pk=parent).get_ancestors(ascending=False, include_self=True)

    template_params = {
        'object_list': branches,
        'bread_crumbs': bread_crumbs
    }

    return render_to_response('b24online/branchList.html', template_params, context_instance=RequestContext(request))


def set_current(request, item_id):
    if item_id != '0':
        try:
            item = Organization.objects.get(pk=item_id)
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('denied'))

        if not item.has_perm(request.user):
            return HttpResponseRedirect(reverse('denied'))

        request.session['current_company'] = item.pk
    else:
        del request.session['current_company']

    return HttpResponseRedirect(request.GET.get('next'), '/')


@csrf_exempt
@login_required
def editor_upload(request):
    form = EditorImageUploadForm(data=request.POST, files=request.FILES)

    if form.is_valid():
        image_path = form.save()

        return JsonResponse({'image': {'url': urljoin(settings.MEDIA_URL, image_path)}})

    return JsonResponse({'error': {'message': form.errors.get('file', [])[0]}})


@csrf_protect
def feedback_form(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            subject = "B24online.com: New message from {0}".format(cd['username'])
            #print(subject, cd['message'], cd['email'], cd['co_email'])
            mail = EmailMessage(subject, cd['message'], cd['email'], cd['co_email'])
            mail.send()
            return JsonResponse({}, status=200)
        else:
            #print(form.errors)
            return JsonResponse({}, status=403)
    else:
        return HttpResponseNotFound()

