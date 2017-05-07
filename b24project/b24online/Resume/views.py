from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from b24online.cbv import ItemsList, ItemDetail, ItemUpdate, ItemCreate, ItemDeactivate
from jobs.models import Resume
from b24online.Resume.forms import ResumeForm, WorkPositionFormSet


class ResumeList(ItemsList):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResumeList, self).dispatch(*args, **kwargs)

    # pagination url
    url_paginator = "resume:paginator"
    url_my_paginator = "resume:my_main_paginator"



    addUrl = 'resume:add'

    # allowed filter list
    # filter_list = []

    @property
    def current_section(self):
        return _("Resume")

    model = Resume

    def ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Resume/contentPage.html'

    def no_ajax(self, request, *args, **kwargs):
        self.template_name = 'b24online/Resume/index.html'

    def optimize_queryset(self, queryset):
        return queryset.select_related('user__profile')

    def get_queryset(self):
        queryset = super(ResumeList, self).get_queryset()

        if self.is_my():
            current_org = self._current_organization

            if current_org is not None:
                queryset = queryset.none()
            else:
                queryset = self.model.get_active_objects().filter(user=self.request.user)

        # https://sentry.ssilaev.com/sentry/b24onlinecom/issues/894/
        # 'SearchEngine' object has no attribute 'order_by'
        #return queryset.order_by(*self._get_sorting_params())
        return queryset


class ResumeDetail(ItemDetail):
    model = Resume
    template_name = 'b24online/Resume/detailContent.html'

    current_section = _('Resume')
    addUrl = 'resume:add'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ResumeDetail, self).dispatch(*args, **kwargs)


class ResumeDelete(ItemDeactivate):
    model = Resume


class ResumeCreate(ItemCreate):
    org_required = False
    model = Resume
    form_class = ResumeForm
    template_name = 'b24online/Resume/addForm.html'
    success_url = reverse_lazy('resume:main')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        work_position_form = WorkPositionFormSet()

        return self.render_to_response(self.get_context_data(form=form, work_position_form=work_position_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        work_position_form = WorkPositionFormSet(self.request.POST)

        if form.is_valid() and work_position_form.is_valid():
            return self.form_valid(form, work_position_form)
        else:
            return self.form_invalid(form, work_position_form)

    def form_valid(self, form, work_position_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.user = self.request.user
        form.instance.updated_by = self.request.user

        for i in range(1, 4):
            company = "company_exp_%s" % i
            position = "position_exp_%s" % i
            start_date = "start_date_exp_%s" % i
            end_date = "end_date_exp_%s" % i

            setattr(form.instance, company, None)
            setattr(form.instance, position, None)
            setattr(form.instance, start_date, None)
            setattr(form.instance, end_date, None)

        for i, cleaned_data in enumerate(work_position_form.cleaned_data, start=1):
            if not cleaned_data:
                continue

            company = "company_exp_%s" % i
            position = "position_exp_%s" % i
            start_date = "start_date_exp_%s" % i
            end_date = "end_date_exp_%s" % i

            setattr(form.instance, company, cleaned_data['company_name'])
            setattr(form.instance, position, cleaned_data['position'])
            setattr(form.instance, start_date, cleaned_data['start_work'])
            setattr(form.instance, end_date, cleaned_data['end_work'])

        self.object = form.save()
        self.object.reindex()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, work_position_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_data = self.get_context_data(form=form, work_position_form=work_position_form)
        return self.render_to_response(context_data)


class ResumeUpdate(ItemUpdate):
    model = Resume
    form_class = ResumeForm
    template_name = 'b24online/Resume/addForm.html'
    success_url = reverse_lazy('resume:main')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        work_position_form = WorkPositionFormSet(initial=[
            {
                'company_name': self.object.company_exp_1,
                'position': self.object.position_exp_1,
                'start_work': self.object.start_date_exp_1,
                'end_work': self.object.end_date_exp_1
            },
            {
                'company_name': self.object.company_exp_2,
                'position': self.object.position_exp_2,
                'start_work': self.object.start_date_exp_2,
                'end_work': self.object.end_date_exp_2
            },
            {
                'company_name': self.object.company_exp_3,
                'position': self.object.position_exp_3,
                'start_work': self.object.start_date_exp_3,
                'end_work': self.object.end_date_exp_3
            }
        ])

        return self.render_to_response(self.get_context_data(form=form, work_position_form=work_position_form))

    def post(self, request, *args, **kwargs):
        """
            Handles POST requests, instantiating a form instance and its inline
            formsets with the passed POST variables and then checking them for
            validity.
            """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        work_position_form = WorkPositionFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and work_position_form.is_valid():
            return self.form_valid(form, work_position_form)
        else:
            return self.form_invalid(form, work_position_form)

    def form_valid(self, form, work_position_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        form.instance.updated_by = self.request.user

        for i in range(1, 4):
            company = "company_exp_%s" % i
            position = "position_exp_%s" % i
            start_date = "start_date_exp_%s" % i
            end_date = "end_date_exp_%s" % i

            setattr(form.instance, company, None)
            setattr(form.instance, position, None)
            setattr(form.instance, start_date, None)
            setattr(form.instance, end_date, None)

        for i, cleaned_data in enumerate(work_position_form.cleaned_data, start=1):
            if not cleaned_data:
                continue

            company = "company_exp_%s" % i
            position = "position_exp_%s" % i
            start_date = "start_date_exp_%s" % i
            end_date = "end_date_exp_%s" % i

            setattr(form.instance, company, cleaned_data['company_name'])
            setattr(form.instance, position, cleaned_data['position'])
            setattr(form.instance, start_date, cleaned_data['start_work'])
            setattr(form.instance, end_date, cleaned_data['end_work'])

        self.object = form.save()

        if form.changed_data:
            self.object.reindex()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, work_position_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """

        return self.render_to_response(self.get_context_data(form=form, work_position_form=work_position_form))
