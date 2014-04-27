
from appl.models import UserSites, Resume, Cabinet, Organization
from appl import func
from core.tasks import addNewSite
from core.models import Dictionary, Item
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from tppcenter.forms import ItemForm
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
        result = _resumeDetailContent(request, item_id)
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
        items_perms = func.getUserPermsForObjectsList(request.user, [site.pk], UserSites.__name__)
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






def _resumeDetailContent(request, item_id):

    resume = get_object_or_404(Resume, pk=item_id)


    attr = (
        'NAME', 'BIRTHDAY', 'MARITAL_STATUS', 'NATIONALITY', 'TELEPHONE_NUMBER','ADDRESS', 'FACULTY', 'PROFESSION',
        'STUDY_START_DATE', 'STUDY_END_DATE', 'STUDY_FORM', 'COMPANY_EXP_1', 'COMPANY_EXP_2','COMPANY_EXP_3',
        'POSITION_EXP_1', 'POSITION_EXP_2', 'POSITION_EXP_3', 'START_DATE_EXP_1', 'START_DATE_EXP_2','START_DATE_EXP_3',
        'END_DATE_EXP_1', 'END_DATE_EXP_2', 'END_DATE_EXP_3', 'ADDITIONAL_STUDY', 'LANGUAGE_SKILL','COMPUTER_SKILL',
        'ADDITIONAL_SKILL', 'SALARY', 'ADDITIONAL_INFORMATION', 'INSTITUTION'
    )

    resumeValues = resume.getAttributeValues(*attr)

    title = resumeValues.get('NAME', False)[0] if resumeValues.get('NAME', False) else ""


    template = loader.get_template('Resume/detailContent.html')

    templateParams = {
       'resumeValues': resumeValues,
       'item_id': item_id
        }

    context = RequestContext(request, templateParams)
    rendered = template.render(context)



    return rendered, title



@login_required(login_url='/login/')
def resumeForm(request, action, item_id=None):
    if item_id:
       if not UserSites.active.get_active().filter(pk=item_id).exists():
         return HttpResponseNotFound()


    current_section = _("Site")
    sitePage = ''

    if action == 'delete':
        sitePage = deleteResume(request, item_id)

    if action == 'add':
        sitePage = addSite(request)

    if action == 'update':
        sitePage = updateSite(request, item_id)

    if isinstance(sitePage, HttpResponseRedirect) or isinstance(sitePage, HttpResponse):
        return sitePage

    templateParams = {
        'sitePage': sitePage,
        'current_section': current_section
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

        user = request.user

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('UserSites', values=values)
        form.clean()


        if form.is_valid():
            site = Site.objects.filter(domain=values['NAME'][0] + '.tppcenter.com')
            if not site.exists():

                func.notify("item_creating", 'notification', user=request.user)
                addNewSite(request.POST, request.FILES, user, current_organization,  lang_code=settings.LANGUAGE_CODE)
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





    if request.POST:
        user = request.user

        values = {}
        values.update(request.POST)
        values.update(request.FILES)

        form = ItemForm('UserSites', values=values, id=item_id)
        form.clean()

        if form.is_valid():
            site = Site.objects.filter(domain=values['NAME'][0] + '.tppcenter.com')

            if not site.exists() or UserSites.objects.filter(sites__id__in=site, organization=current_organization).exists():
                func.notify("item_creating", 'notification', user=request.user)
                addNewSite(request.POST, request.FILES, user, current_organization,  item_id=item_id,
                                   lang_code=settings.LANGUAGE_CODE)

                return HttpResponseRedirect(reverse('site:main'))
            else:
                  form.errors.update({"NAME": _("This domain is used, please try something else")})

    template = loader.get_template('UserSites/addForm.html')

    templateParams = {

        'form': form,

    }

    context = RequestContext(request, templateParams)
    sitePage = template.render(context)

    return sitePage



def deleteResume(request, item_id):


    instance = Resume.objects.get(pk=item_id)
    instance.activation(eDate=now())
    instance.end_date = now()





    return HttpResponseRedirect(reverse('resume:main'))



