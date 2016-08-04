from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy

from b24online.models import Profile
from b24online.Profile.forms import ProfileForm
from b24online.cbv import ItemUpdate


class ProfileUpdate(ItemUpdate):
    model = Profile
    form_class = ProfileForm
    template_name = 'b24online/Profile/addForm.html'
    success_url = reverse_lazy('profile:main')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return Profile.objects.create(user=self.request.user)

    def form_valid(self, form):
        cd = form.cleaned_data
        form.instance.birthday = cd.get('birthday', None)
        form.instance.metadata['facebook'] = cd.get('facebook', None)
        form.instance.metadata['linkedin'] = cd.get('linkedin', None)
        form.instance.metadata['co'] = cd.get('co', None)
        form.instance.metadata['co_slogan'] = cd.get('co_slogan', None)
        form.instance.metadata['co_description'] = cd.get('co_description', None)
        result = super().form_valid(form)

        if form.changed_data:
            self.object.reindex()

            if 'avatar' in form.changed_data:
                self.object.upload_images()

        return result
