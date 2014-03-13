__author__ = 'user'
from django.shortcuts import render_to_response
from appl import func
from django.conf import settings
from django.utils.translation import ugettext as _
from appl.models import Notification

def about(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user


    templateParams = {

        'current_section': _('About'),

        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/about.html", templateParams)

def how(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('How the system works'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/how.html", templateParams)

def terms(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Terms of use'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/terms.html", templateParams)

def partner(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Find a Business Partner'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/partner.html", templateParams)

def privacy(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Privacy'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/privacy.html", templateParams)

def shop(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Create online shop'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/shop.html", templateParams)

def event(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Post announcement event'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/event.html", templateParams)

def proposal(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user


    templateParams = {

        'current_section': _('Add a business proposal'),

        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/proposal.html", templateParams)

def contact(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Contact us'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft,
    }

    return render_to_response("Project/contact.html", templateParams)

def community(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('Ask the community'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/community.html", templateParams)

def faq(request):

    bRight = func.getBannersRight(request, ['Right 1', 'Right 2'], settings.SITE_ID, 'AdvBanner/banners.html')
    bLeft = func.getBannersRight(request, ['Left 1', 'Left 2', 'Left 3'], settings.SITE_ID, 'AdvBanner/banners.html')

    user = request.user
    if user.is_authenticated():
        notification = Notification.objects.filter(user=request.user, read=False).count()
        if not user.first_name and not user.last_name:
            user_name = user.email
        else:
            user_name = user.first_name + ' ' + user.last_name
    else:
        user_name = None
        notification = None

    templateParams = {
        'user_name': user_name,
        'current_section': _('FAQ'),
        'notification': notification,
        'bannerRight': bRight,
        'bannerLeft': bLeft
    }

    return render_to_response("Project/faq.html", templateParams)