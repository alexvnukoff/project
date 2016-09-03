from django.shortcuts import get_object_or_404, render

from b24online.models import StaticPage


def project(request, template, section):
    template_params = {
        'current_section': section,
    }

    return render(request, "b24online/Project/" + template, template_params)


def show_page(request, item_id=None, slug=None):
    page = get_object_or_404(StaticPage, pk=item_id)

    return render(request, "b24online/Project/detail.html", {'page': page})
