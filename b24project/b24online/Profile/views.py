# -*- encoding: utf-8 -*-
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from b24online.models import Profile
from b24online.Profile.forms import ProfileForm, AvatarForm, ImageForm
from b24online.cbv import ItemUpdate
from django.http import JsonResponse, HttpResponse


class ProfileView(ItemUpdate):
    model = Profile
    template_name = 'b24online/Profile/Profile.html'
    success_url = reverse_lazy('profile:main')

    form_class = ProfileForm
    second_form_class = AvatarForm
    third_form_class = ImageForm

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        if 'form' not in context:
            context['form'] = self.form_class(initial={
                'facebook': self.get_object().facebook,
                'linkedin': self.get_object().linkedin,
                'twitter': self.get_object().twitter,
                'instagram': self.get_object().instagram,
                'youtube': self.get_object().youtube,
                'gplus': self.get_object().gplus,
                'vkontakte': self.get_object().vkontakte,
                'odnoklassniki': self.get_object().odnoklassniki,
                'co_name': self.get_object().co_name,
                'co_slogan': self.get_object().co_slogan,
                'co_description': self.get_object().co_description,
                'co_phone': self.get_object().co_phone,
                'co_fax': self.get_object().co_fax
                })

        if 'form1' not in context:
            context['form1'] = self.second_form_class(initial={'avatar': self.get_object().avatar })

        if 'form2' not in context:
            context['form2'] = self.third_form_class(initial={'image': self.get_object().image })
        return context

    def form_invalid(self, **kwargs):
        if self.request.is_ajax():
            return HttpResponse(status=403)
        else:
            return self.render_to_response(self.get_context_data(**kwargs))

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Profile.objects.create(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # get the user instance
        self.object = self.get_object()

        if 'form' in request.POST:
            form_class = self.get_form_class()
            form_name = 'form'

        elif 'form1' in request.POST:
            form_class = self.second_form_class
            form_name = 'form1'

        else:
            form_class = self.third_form_class
            form_name = 'form2'

        form = self.get_form(form_class)

        if form.is_valid():
            cd = form.cleaned_data

            if 'form' in request.POST:
                form.instance.birthday = cd.get('birthday', None)
                form.instance.metadata['facebook'] = cd.get('facebook', None)
                form.instance.metadata['linkedin'] = cd.get('linkedin', None)
                form.instance.metadata['twitter'] = cd.get('twitter', None)
                form.instance.metadata['instagram'] = cd.get('instagram', None)
                form.instance.metadata['youtube'] = cd.get('youtube', None)
                form.instance.metadata['gplus'] = cd.get('gplus', None)
                form.instance.metadata['vkontakte'] = cd.get('vkontakte', None)
                form.instance.metadata['odnoklassniki'] = cd.get('odnoklassniki', None)
                form.instance.metadata['co_phone'] = cd.get('co_phone', None)
                form.instance.metadata['co_fax'] = cd.get('co_fax', None)

            result = super().form_valid(form)
            if form.changed_data:
                self.object.reindex()

                if 'avatar' in cd:
                    self.object.upload_images('avatar')
                    if request.is_ajax():
                        return JsonResponse({ 'avatar': self.get_object().avatar.big })

                if 'image' in cd:
                    self.object.upload_images('image')
                    if request.is_ajax():
                        return JsonResponse({ 'image': self.get_object().image.big })

            return result
        else:
            return self.form_invalid(**{form_name: form})


class ChangePassword(FormView):
    model = Profile
    form_class = SetPasswordForm
    template_name = 'b24online/Profile/changePassword.html'
    success_url = reverse_lazy('profile:change_password_done')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChangePassword, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ChangePassword, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(ChangePassword, self).form_valid(form)

