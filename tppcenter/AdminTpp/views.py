from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.utils.timezone import now
from appl.models import Cabinet, AdvertisementItem, AdvOrder, Country, AdvBannerType, topTypes, staticPages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from haystack.query import SearchQuerySet
from core.models import Item, User, Relationship
from dateutil.parser import parse
from django.contrib.sites.models import Site
import json
from tpp.settings import MEDIA_URL
from tppcenter.forms import ItemForm
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


@login_required(login_url="/login/")
def dashboard(request):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    templateParams = {}
    return render_to_response("AdminTpp/index.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url="/login/")
def users(request):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    cols = ['name', 'email', 'date_joined', 'last_login', 'date_joined', 'ip']

    if request.is_ajax():
        orderby = []

        displayStart = int(request.GET.get('iDisplayStart', 1))
        displayLen = int(request.GET.get('iDisplayLength', 10))

        if displayStart == 1:
            page = 1
        else:
            page = int(displayStart / displayLen + 1)

        sortCol_0 = int(request.GET.get('iSortCol_0', 0))
        sortingCols = int(request.GET.get('iSortingCols', 0))

        if sortCol_0 > 0:
            for x in range(0, sortingCols):
                colIndex = request.GET.get('iSortCol_' + str(x), False)

                if colIndex is not False:
                    colIndex = int(colIndex)

                    dir = request.GET.get('sSortDir_' + str(x), 'desc')

                    if dir == 'asc':
                        orderby.append(cols[colIndex])
                    else:
                        orderby.append('-' + cols[colIndex])

        search = request.GET.get('sSearch', "").strip()



        if search != "":
            sqs = SearchQuerySet().models(Cabinet).filter(text=search)
        else:
            sqs = SearchQuerySet().models(Cabinet)

        paginator = Paginator(sqs, 10)

        try:
            onPage = paginator.page(page)
        except Exception:
            onPage = paginator.page(1)

        cabinets = [itm.id for itm in onPage.object_list]

        ItemsWithValues = Item.getItemsAttributesValues(('LAST_NAME', 'FIRST_NAME', 'MIDDLE_NAME'), cabinets)
        users = User.objects.filter(cabinet__pk__in=cabinets).values('email', 'last_login', 'date_joined', 'ip', 'cabinet').order_by('email')



        for values in users:

            cabinet = int(values['cabinet'])

            if cabinet not in ItemsWithValues or not isinstance(ItemsWithValues[cabinet], dict):
                ItemsWithValues[cabinet] = {}

            ItemsWithValues[cabinet].update(values)

        resultData = []

        for pk, cabinet in ItemsWithValues.items():
            resultNode = []
            #Full name
            name = [cabinet.get('LAST_NAME', [""])[0],
                    cabinet.get('MIDDLE_NAME', [""])[0],
                    cabinet.get('FIRST_NAME', [""])[0]]

            #Creating list of result data
            resultNode.append(" ".join(name))
            resultNode.append(cabinet.get('email', ""))
            resultNode.append(cabinet.get('last_login', "").strftime('%Y-%m-%dT%H:%M:%S'))
            resultNode.append(cabinet.get('date_joined', "").strftime('%Y-%m-%dT%H:%M:%S'))
            resultNode.append(cabinet.get('ip', ""))

            resultData.append(resultNode)


        return HttpResponse(json.dumps({
            "sEcho": int(request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData" : resultData
        }))
    else:
        templateParams = {}
        return render_to_response("AdminTpp/users.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url="/login/")
def adv(request):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    if request.is_ajax():
        ads = AdvertisementItem.objects.all().order_by('-create_date')

        displayStart = int(request.GET.get('iDisplayStart', 1))
        displayLen = int(request.GET.get('iDisplayLength', 10))

        if displayStart == 1:
            page = 1
        else:
            page = int(displayStart / displayLen + 1)

        paginator = Paginator(ads, 10)

        advOnPage = paginator.page(page)

        advIDs = [adv.pk for adv in advOnPage.object_list]

        owners = Relationship.objects.filter(child__in=advIDs, type="dependence").values('parent', 'child')

        advToOwner = {}
        idsForAttr = advIDs

        for ownerDict in owners:
            advToOwner[ownerDict['child']] = ownerDict['parent']
            idsForAttr.append(ownerDict['parent'])

        advAttrValues = Item.getItemsAttributesValues(('COST', 'IMAGE', 'END_EVENT_DATE',
                                                       'START_EVENT_DATE', 'NAME'), idsForAttr)

        jsonResponse = {
            'aaData': [],
            "sEcho": int(request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count
        }

        for advObj in advOnPage.object_list:

            if advObj.pk not in advAttrValues or not isinstance(advAttrValues[advObj.pk], dict):
                advAttr = {}
                advAttrValues[advObj.pk] = {}
            else:
                advAttr = advAttrValues[advObj.pk]

            end_event_date = parse(advAttr.get('END_EVENT_DATE', [None])[0]).strftime("%Y-%m-%d")
            start_event_date = parse(advAttr.get('START_EVENT_DATE', [None])[0]).strftime("%Y-%m-%d")

            if not end_event_date:
                active = 0
            else:
                active = 1 if (end_event_date == advObj.end_date.strftime("%Y-%m-%d")) else 0

            if getattr(advObj, 'adv_top', None):
                type = 'Top'
            else:
                type = 'Banner'

            owner = advToOwner.get(advObj.pk, 0)

            if owner not in advAttrValues or not isinstance(advAttrValues[owner], dict):
                owner = {}
            else:
                owner = advAttrValues[owner]

            image = advAttr.get('IMAGE', [""])[0]

            if len(image) > 0:
                image = MEDIA_URL + 'original/' + image

            jsonResponse['aaData'].append([
                type,
                owner.get('NAME', [""])[0],
                "",
                start_event_date,
                end_event_date,
                active,
                float(advAttr.get('COST', [0])[0]),
                advObj.pk,
                image

            ])

        return HttpResponse(json.dumps(jsonResponse))

    else:
        templateParams = {}
        return render_to_response("AdminTpp/adv.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url="/login/")
def advActivate(request, advID):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    ad = get_object_or_404(AdvertisementItem, pk=advID)

    end_date = ad.getAttributeValues('END_EVENT_DATE')

    ad.end_date = parse(end_date[0])
    ad.save()

    return HttpResponseRedirect(reverse("AdminTpp:adv"))

@login_required(login_url="/lgoin/")
def advDeactivate(request, advID):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()


    ad = get_object_or_404(AdvertisementItem, pk=advID)

    ad.end_date = now()
    ad.save()

    return HttpResponseRedirect(reverse("AdminTpp:adv"))

@login_required(login_url="/lgoin/")
def advTargets(request, advID):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()


    order = get_object_or_404(AdvOrder, c2p__parent=advID)

    ordWithValues = order.getAttributeValues('ORDER_HISTORY', 'ORDER_DAYS', 'COST', 'START_EVENT_DATE', 'END_EVENT_DATE')

    ordJson = ordWithValues.get('ORDER_HISTORY', [""])[0]

    orderHistory = json.loads(ordJson)

    ids = orderHistory.get('ids', [])

    placeNames = Item.getItemsAttributesValues('NAME', ids)

    nameCostDict = {}

    for pid, cost in orderHistory.get('costs', {}).items():



        if int(pid) in placeNames:
            attrValues = placeNames[int(pid)]
        else:
            attrValues = {}

        if isinstance(attrValues, int):
            attrValues = {}

        nameCostDict.update({
            attrValues.get('NAME', [""])[0] : cost
        })

    startDate = parse(ordWithValues.get('START_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')
    endDate = parse(ordWithValues.get('END_EVENT_DATE', [""])[0]).strftime('%d/%m/%Y')


    templateParams = {
        'nameCost': nameCostDict,
        'totalCost': ordWithValues.get('COST', [0])[0],
        'startDate': startDate,
        'endDate': endDate,
        'totalDays': ordWithValues.get('ORDER_DAYS', [0])[0],
    }

    return render_to_response('adminTpp/targetsList.html', templateParams, context_instance=RequestContext(request))


@login_required(login_url="/login/")
def adv_price(request, ladModel=None):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    cols = ['name', 'price', 'save']

    if request.is_ajax() and ladModel:
        orderby = []

        displayStart = int(request.GET.get('iDisplayStart', 1))
        displayLen = int(request.GET.get('iDisplayLength', 10))

        if displayStart == 1:
            page = 1
        else:
            page = int(displayStart / displayLen + 1)

        sortCol_0 = int(request.GET.get('iSortCol_0', 0))
        sortingCols = int(request.GET.get('iSortingCols', 0))

        if sortCol_0 > 0:
            for x in range(0, sortingCols):
                colIndex = request.GET.get('iSortCol_' + str(x), False)

                if colIndex is not False:
                    colIndex = int(colIndex)

                    dir = request.GET.get('sSortDir_' + str(x), 'desc')

                    if dir == 'asc':
                        orderby.append(cols[colIndex])
                    else:
                        orderby.append('-' + cols[colIndex])

        search = request.GET.get('sSearch', "").strip()



        if search != "":
            sqs = SearchQuerySet().models(ladModel).filter(title_auto=search)
        else:
            sqs = SearchQuerySet().models(ladModel)

        paginator = Paginator(sqs, 10)

        try:
            onPage = paginator.page(page)
        except Exception:
            onPage = paginator.page(1)

        country_ids = [itm.id for itm in onPage.object_list]

        ItemsWithValues = Item.getItemsAttributesValues(('NAME', 'COST'), country_ids)

        resultData = []

        for pk, country in ItemsWithValues.items():

            #Full name
            name = country.get('NAME', [""])[0]
            cost = float(country.get('COST', [0.0])[0])

            #Creating list of result data
            resultNode = [name, cost, pk]

            resultData.append(resultNode)


        return HttpResponse(json.dumps({
            "sEcho": int(request.GET.get('sEcho', 1)),
            "iTotalRecords": paginator.count,
            "iTotalDisplayRecords": paginator.count,
            "aaData" : resultData
        }))
    else:
        templateParams = {}
        return render_to_response("AdminTpp/prices.html", templateParams, context_instance=RequestContext(request))

@login_required(login_url="/login/")
def adv_save_price(request):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    price = float(request.POST.get('price', 0))
    item = int(request.POST.get('id', 0))

    if item > 0:
        item = Item.objects.get(pk=item)

        item.setAttributeValue({'COST': price}, request.user)

    return HttpResponse()

@login_required(login_url="/login/")
def adv_settings(request):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()


    if request.is_ajax():

        if request.POST:

            type = request.POST.get('type', 'banner')

            if type == 'banner':
                _add_update_banner_type(request)
            else:
                pk = int(request.POST.get('pk', None))
                factor = int(request.POST.get('factor', 1))

                if pk:
                    try:
                        top = topTypes.objects.get(pk=pk)

                        top.setAttributeValue({'COST': factor}, request.user)
                    except ObjectDoesNotExist:
                        pass

            return HttpResponse()
        else:
            displayStart = int(request.GET.get('iDisplayStart', 1))
            displayLen = int(request.GET.get('iDisplayLength', 10))

            if displayStart == 1:
                page = 1
            else:
                page = int(displayStart / displayLen + 1)

            types = AdvBannerType.objects.all()

            paginator = Paginator(types, 10)

            try:
                onPage = paginator.page(page)
            except Exception:
                onPage = paginator.page(1)

            country_ids = [itm.id for itm in onPage.object_list]

            ItemsWithValues = Item.getItemsAttributesValues(('NAME', 'COST', 'WIDTH', 'HEIGHT'), country_ids)

            resultData = []

            for type in onPage.object_list:

                if type.pk not in ItemsWithValues:
                    ItemsWithValues[type.pk] = {}
                elif not isinstance(ItemsWithValues[type.pk], dict):
                    ItemsWithValues[type.pk] = {}

                attrs = ItemsWithValues[type.pk]

                #Full name
                name = attrs.get('NAME', [""])[0]
                factor = float(attrs.get('COST', [0.0])[0])
                width = attrs.get('WIDTH', [0])[0]
                height = attrs.get('HEIGHT', [0])[0]

                branch = 1 if type.enableBranch else 0
                country = 1 if type.enableCountry else 0
                tpp = 1 if type.enableTpp else 0
                site = type.sites.all()[0].name

                #Creating list of result data
                resultNode = [name, site, factor, branch, country, tpp, width, height, type.title, type.pk]

                resultData.append(resultNode)


            return HttpResponse(json.dumps({
                "sEcho": int(request.GET.get('sEcho', 1)),
                "iTotalRecords": paginator.count,
                "iTotalDisplayRecords": paginator.count,
                "aaData" : resultData
            }))
    else:

        result = False

        if request.POST:
            result = _add_update_banner_type(request)

        sites = {}

        for site in Site.objects.all():
            sites.update({site.pk: site.name})

        tops = [top.pk for top in topTypes.objects.all()]

        topAttr = Item.getItemsAttributesValues(('COST', 'NAME'), tops)

        templateParams = {'sites': sites, 'result': None, 'tops': topAttr}

        if not isinstance(result, bool):
            templateParams['result'] = result

        return render_to_response("AdminTpp/adv_sett.html", templateParams, context_instance=RequestContext(request))


def _add_update_banner_type(request):

    form = None

    if request.POST:

        user = request.user

        pk = request.POST.get('pk', None)

        if pk:

            try:
                type = AdvBannerType.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return form

        values = {
            'NAME': request.POST.get('name', ""),
            'WIDTH': int(request.POST.get('width', 0)),
            'HEIGHT': int(request.POST.get('height', 0))
        }

        code = request.POST.get('code', "")
        site = request.POST.get('site', 0)
        tpp = True if request.POST.get('tpp', False) else False
        country = True if request.POST.get('country', False) else False
        branch = True if request.POST.get('branch', False) else False

        form = ItemForm('AdvBannerType', values=values)
        form.clean()

        if form.is_valid():

            if pk:
                if not AdvBannerType.objects.filter(title=code, pk=pk).exists() and AdvBannerType.objects.filter(title=code).exists():
                    form.errors.update({"CODE": _("Banner type already exists")})
            elif AdvBannerType.objects.filter(title=code).exists():
                form.errors.update({"CODE": _("Banner type already exists")})

            if not pk and not Site.objects.filter(pk=site).exists():
                form.errors.update({"SITE": _("Invalid site")})

            if values['HEIGHT'] <= 0:
                form.errors.update({"HEIGHT": _("Invalid height")})

            if values['WIDTH'] <= 0:
                form.errors.update({"WIDTH": _("Invalid width")})

            if not branch and not tpp and not country:
                form.errors.update({"TARGET": _("Invalid targeting")})

            if len(code) == 0:
                form.errors.update({"CODE": _("Invalid code")})

            if form.is_valid():
                if not pk:
                    type = form.save(user, site, disableNotify=True)
                else:
                    type.setAttributeValue(values, user)

                type.title = code
                type.enableCountry = country
                type.enableTpp = tpp
                type.enableBranch = branch
                type.save()

                return True



        return form

    return False

@login_required(login_url="/login/")
def adv_remove_banner_type(request, typeID):


    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()


    ad = get_object_or_404(AdvBannerType, pk=typeID)
    ad.delete()


    return HttpResponseRedirect(reverse("AdminTpp:adv_sett"))

@login_required(login_url="/login/")
def pages_delete(request, pk):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    obj = get_object_or_404(staticPages, pk=pk)

    obj.delete()

    return HttpResponseRedirect(reverse("AdminTpp:pages"))

@login_required(login_url="/login/")
def pages(request, editPage=None):

    if not request.user.is_commando and not request.user.is_superuser:
        return HttpResponseBadRequest()

    PAGE_TYPES = dict(staticPages.PAGE_TYPES)

    if editPage:
        obj = get_object_or_404(staticPages, pk=editPage)


    if request.is_ajax():

        if request.POST:
            name = request.POST.get('NAME', "")
            onTop = True if request.POST.get('onTop', False) else False

            if len(name) > 0:
                obj.onTop = onTop
                obj.save()
                obj.setAttributeValue({'NAME': name}, request.user)

            return HttpResponse()
        else:

            displayStart = int(request.GET.get('iDisplayStart', 1))
            displayLen = int(request.GET.get('iDisplayLength', 10))

            if displayStart == 1:
                page = 1
            else:
                page = int(displayStart / displayLen + 1)

            pages = staticPages.objects.all()

            paginator = Paginator(pages, 10)

            try:
                onPage = paginator.page(page)
            except Exception:
                onPage = paginator.page(1)

            pages_ids = [itm.id for itm in onPage.object_list]

            ItemsWithValues = Item.getItemsAttributesValues(('NAME', 'DESCRIPTION'), pages_ids)

            resultData = []

            for page in onPage.object_list:

                if page.pk not in ItemsWithValues:
                    ItemsWithValues[page.pk] = {}
                elif not isinstance(ItemsWithValues[page.pk], dict):
                    ItemsWithValues[page.pk] = {}

                attrs = ItemsWithValues[page.pk]

                #Full name
                name = attrs.get('NAME', [""])[0]

                #Creating list of result data
                resultNode = [name, int(page.onTop), PAGE_TYPES[page.pageType], page.pk]

                resultData.append(resultNode)


            return HttpResponse(json.dumps({
                    "sEcho": int(request.GET.get('sEcho', 1)),
                    "iTotalRecords": paginator.count,
                    "iTotalDisplayRecords": paginator.count,
                    "aaData" : resultData
            }))
    else:

        form = None

        user = request.user
        type = ''

        if request.POST:

            values = {
                'NAME': request.POST.get('NAME', ""),
                'DETAIL_TEXT':  request.POST.get('DETAIL_TEXT', "")
            }

            form = ItemForm('staticPages', values=values)
            form.clean()

            onTop = request.POST.get('onTop', None)

            if onTop is not None:
                onTop = True if onTop else False

            type = request.POST.get('type', None)

            if form.is_valid():

                if not type or type not in PAGE_TYPES:
                    form.errors.update({'TYPE': _('Invalid type')})


                if form.is_valid():
                    if editPage:
                        page = obj
                        page.setAttributeValue(values, user)
                    else:
                        page = form.save(user, settings.SITE_ID, disableNotify=True)

                    if onTop is not None:
                        page.onTop = onTop

                    page.pageType = type
                    page.save()

                    return HttpResponseRedirect(reverse("AdminTpp:pages"))

        elif editPage:

            type = obj.pageType
            attr = obj.getAttributeValues('NAME', 'DETAIL_TEXT')

            values = {
                'NAME': attr.get('NAME', [""])[0],
                'DETAIL_TEXT':  attr.get('DETAIL_TEXT', [""])[0]
            }

            form = ItemForm('staticPages', values=values)


        templateParams = {'types': staticPages.PAGE_TYPES, 'form': form, 'selectedType': type}

        return render_to_response("AdminTpp/pages.html", templateParams, context_instance=RequestContext(request))






