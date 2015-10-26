import os

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from b24online.models import Banner

from centerpokupok.models import B2CProductCategory, B2CProduct


class SiteSettings(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        result = {
            'slides': self._get_slider_list(),
            'categories': self._get_categories_list(),
            'contacts': self._get_contacts(),
            'footerBanner': self._get_foot_banner(),
            'orgLogo': get_current_site(self.request).user_site.organization.logo.big,
            'logo': get_current_site(self.request).user_site.logo.big
        }

        banners = self._get_banners()

        if banners:
            result['offerIcons'] = banners

        point = self._get_map_point()

        if point:
            result['map'] = point

        return Response(result)

    def _get_slider_list(self):
        import glob
        user_site = get_current_site(self.request).user_site
        custom_images = user_site.slider_images

        if custom_images:
            images = [{'url': obj.image.original} for obj in custom_images.only('image')]
        else:
            static_url = "%susersites/templates" % settings.STATIC_URL
            dir = user_site.template.folder_name
            images = [{'url': "%s/%s/%s" % (static_url, os.path.basename(dir), os.path.basename(image))}
                      for image in glob.glob(dir + "/*.jpg")]

        return images

    def _get_categories_list(self):
        organization = get_current_site(self.request).user_site.organization
        categories = B2CProductCategory.objects.filter(products__company_id=organization.pk) \
            .order_by('level').distinct()

        result = []

        for _, cat in sorted(self._load_category_hierarchy(categories).items(), key=lambda x: [x[1].tree_id, x[1].lft]):
            category = {'name': cat.name, 'id': cat.id}

            if cat.level == 0:
                result.append(category)
            else:
                parent_node = result[-1] if cat.level == 1 else result[-1]['subCategory'][-1]

                if 'subCategory' not in parent_node:
                    parent_node['subCategory'] = []

                parent_node['subCategory'].append(category)

        return result

    def _load_category_hierarchy(self, categories, loaded_categories=None):

        if not loaded_categories:
            loaded_categories = {}

        categories_to_load = []

        for category in categories:
            loaded_categories[category.pk] = category

            if category.parent_id and category.parent_id not in loaded_categories:
                categories_to_load.append(category.parent_id)

        if categories_to_load:
            queryset = B2CProductCategory.objects.filter(pk__in=categories_to_load).order_by('level')
            loaded_categories = self._load_category_hierarchy(queryset, loaded_categories)

        return loaded_categories

    def _get_contacts(self):
        return {
            'orgName': get_current_site(self.request).user_site.organization.name,
            'phone': get_current_site(self.request).user_site.organization.phone,
            'tel': get_current_site(self.request).user_site.organization.phone,
            'email': get_current_site(self.request).user_site.organization.email,
            'address': get_current_site(self.request).user_site.organization.address
        }

    def _get_banners(self):
        site_pk = get_current_site(self.request).pk
        banners = []
        blocks = ('SITES RIGHT 1', 'SITES RIGHT 2', 'SITES RIGHT 3', 'SITES RIGHT 4', 'SITES RIGHT 5')

        for banner in Banner.objects.filter(site_id=site_pk, block__code__in=blocks, block__block_type='user_site'):
            banners.append({'url': banner.link, 'image': banner.image.url, 'title': banner.title})

        return banners

    def _get_map_point(self):
        location = get_current_site(self.request).user_site.organization.location

        if location:
            location = location.split(',')
            return {
                "lat": location[0],
                "longt": location[1]
            }

        return None

    def _get_foot_banner(self):
        site_pk = get_current_site(self.request).pk

        try:
            banner = Banner.objects.get(site_id=site_pk, block__code='SITES FOOTER', block__block_type='user_site')
            return {'url': banner.link, 'image': banner.image.url, 'title': banner.title}
        except ObjectDoesNotExist:
            return None


@api_view(['GET'])
@permission_classes((AllowAny, ))
def actions(request):
    coupons = B2CProduct.get_active_objects().filter(coupon_dates__contains=now().date(), coupon_discount_percent__gt=0) \
                  .order_by("-created_at")[:4]
    result = []

    for product in coupons:
        result.append({
            "name": product.name,
            "oldPrice": product.cost,
            "percent":product.coupon_discount_percent,
            "endDate": product.end_coupon_date,
            "cover": product.image.big if product.image else None,
            "more": "about.html",
            "details": product.short_description if product.short_description else product.description
        })

    return Response(result)