

from core.models import Action, ActionPath, Attribute, Item, Relationship, Dictionary, State, Slot, Process, Value, AttrTemplate

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from core.models import User
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm


    list_display = ('email', 'username', 'is_admin',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('date_of_birth', 'first_name', 'last_name', 'avatar')}),
        ('Permissions', {'fields': ('is_admin',)}),# 'is_active', 'is_staff', 'is_superuser',
                                    #'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'date_of_birth', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class SlotsInLine(admin.TabularInline):
    model = Slot
    extra = 2

class ParentRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "parent"


class ChildtRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "child"

class DictioryAdmin(admin.ModelAdmin):
    fields = ['title']
    inlines = [SlotsInLine]

class AttributesInline(admin.TabularInline):
    model = AttrTemplate
    extra = 5

class ContentAdmin(admin.ModelAdmin):
    inlines = [AttributesInline]

class ValuesInline(admin.TabularInline):
    model = Value
    extra = 5


class ItemAdmin(admin.ModelAdmin):
    inlines = [ParentRelationshipInLIne, ChildtRelationshipInLIne, ValuesInline ]




admin.site.register(User, UserAdmin)
admin.site.register(Action)
admin.site.register(ActionPath)
admin.site.register(Attribute)
admin.site.register(ContentType, ContentAdmin)
admin.site.register(Process)
admin.site.register(Relationship)
admin.site.register(Dictionary, DictioryAdmin)
admin.site.register(State)
admin.site.register(Item, ItemAdmin)
admin.site.register(Value)
#admin.site.register(AttrTemplate)
