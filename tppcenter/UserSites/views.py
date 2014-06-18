
from appl.models import UserSites, Resume,  Organization, ExternalSiteTemplate, Gallery, Company
from appl import func
from core.tasks import addNewSite
from core.models import Item
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm, BasePhotoGallery
from django.forms.models import modelformset_factory
from django.contrib.sites.models import Site


login_required(login_url='/login/')
def get_resume_list(request, page=1, item_id=None, my=None, slug=None):


   # if slug and  not Value.objects.filter(item=item_id, attr__title='SLUG', title=slug).exists():
    #     slug = Value.objects.get(item=item_id, attr__title='SLUG').title
     #    return HttpResponseRedirect(reverse('tenders:detail',  args=[slug]))



    if item_id:
       if not Item.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()








    if item_id is None:
        sitePage = _siteList(request)
    else:
        result = {}
        sitePage = result[0]
        title = result[1]


    templateParams =  {
            'current_section': 'Sites',
            'sitePage': sitePage,
            'addNew': reverse('site:add'),
            'item_id': item_id,

        }

    return render_to_response("UserSites/index.html", templateParams, context_instance=RequestContext(request))


def _siteList(request):
    current_organization = request.session.get('current_company', False)
    if not current_organization:
         return func.emptyCompany()

    try:
        site = UserSites.active.get_active().get(organization=current_organization)
        siteValues = site.getAttributeValues('NAME', 'SLUG')
        items_perms = func.getUserPermsForObjectsList(request.user, [current_organization], Organization.__name__)
    except ObjectDoesNotExist:
        siteValues = ""
        items_perms = ''
        site = None



    template = loader.get_template("UserSites/contentPage.html")
    templateParams = {
        'siteValues': siteValues,
        'current_path': request.get_full_path(),
        'items_perms': items_perms,
        'id': site.pk if site else ""
    }
    context = RequestContext(request, templateParams)
    rendered = template.render(context)

    return rendered










@login_required(login_url='/login/')
def resumeForm(request, action, item_id=None):
    if item_id:
       if not UserSites.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Site")
    sitePage = ''
    templates = ExternalSiteTemplate.active.get_active().all()
    templates_ids = [template.pk for template in templates]
    template_values = Item.getItemsAttributesValues(('NAME', 'TEMPLATE_IMAGE_FOLDER'), templates_ids)

    if action == 'delete':
        sitePage = deleteResume(request, item_id)
    elif action == 'add':
        sitePage = addSite(request)
    elif action == 'update':
        sitePage = updateSite(request, item_id)

    if isinstance(sitePage, HttpResponseRedirect) or isinstance(sitePage, HttpResponse):
        return sitePage

    templateParams = {
        'sitePage': sitePage,
        'current_section': current_section,
        'template_values': template_values
    }

    return render_to_response('UserSites/index.html', templateParams, context_instance=RequestContext(request))


def addSite(request):
    current_organization = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_organization)

    perm_list = item.getItemInstPermList(request.user)


    if 'add_usersites' not in perm_list:
         return func.permissionDenied()





    sites = UserSites.active.get_active().filter(organization=current_organization)

    if sites.count() == 1:
         return func.permissionDenied(message=_('You cannot add more than one site for your organization'))

    form = None


    if request.POST:
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        user = request.user

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('UserSites', values=values)
        form.clean()


        if gallery.is_valid() and form.is_valid():
            site = Site.objects.filter(domain=values['NAME'][0] + '.tppcenter.com')
            if not site.exists():

                func.notify("item_creating", 'notification', user=request.user)
                addNewSite.delay(request.POST, request.FILES, user, current_organization,  lang_code=settings.LANGUAGE_CODE)
                return HttpResponseRedirect(reverse('site:main'))
            else:
                  form.errors.update({"NAME": _("This domain is used, please try something else")})



    template = loader.get_template('UserSites/addForm.html')
    context = RequestContext(request, {'form': form})
    sitePage = template.render(context)

    return sitePage


def updateSite(request, item_id):
    current_organization = request.session.get('current_company', False)

    if not request.session.get('current_company', False):
         return func.emptyCompany()

    item = Organization.objects.get(pk=current_organization)

    perm_list = item.getItemInstPermList(request.user)


    if 'change_usersites' not in perm_list:
         return func.permissionDenied()



    form = ItemForm('UserSites', id=item_id)

    Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
    gallery = Photo(parent_id=item_id)
    photos = ""

    if gallery.queryset:
       photos = [{'photo': image.photo, 'pk': image.pk} for image in gallery.queryset]





    if request.POST:
        user = request.user
        Photo = modelformset_factory(Gallery, formset=BasePhotoGallery, extra=5, fields=("photo",))
        gallery = Photo(request.POST, request.FILES)

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('UserSites', values=values, id=item_id)
        form.clean()

        if gallery.is_valid() and  form.is_valid():
            site = Site.objects.filter(domain=values['NAME'][0] + '.tppcenter.com')

            if not site.exists() or UserSites.objects.filter(sites__id__in=site, organization=current_organization).exists():
                func.notify("item_creating", 'notification', user=request.user)
                addNewSite.delay(request.POST, request.FILES, user, current_organization,  item_id=item_id,
                                   lang_code=settings.LANGUAGE_CODE)

                return HttpResponseRedirect(reverse('site:main'))
            else:
                  form.errors.update({"NAME": _("This domain is used, please try something else")})

    template = loader.get_template('UserSites/addForm.html')

    templateParams = {

        'form': form,
        'gallery': gallery,
        'photos': photos,

    }

    context = RequestContext(request, templateParams)
    sitePage = template.render(context)

    return sitePage



def deleteResume(request, item_id):


    instance = Resume.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()





    return HttpResponseRedirect(reverse('resume:main'))



