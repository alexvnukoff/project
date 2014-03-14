from core.models import Action, ActionPath, Attribute, Item, Relationship, Dictionary, State, Slot, Process, Value, AttrTemplate
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from core.models import User
from core.forms import *

class TPPUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm


    list_display = ('email', 'username', 'is_admin',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'avatar', 'date_of_birth',)}),
        ('Permissions', {'fields': ('is_manager', 'is_admin', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'date_of_birth')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
    raw_id_fields = ("groups",)

class SlotsInLine(admin.TabularInline):
    model = Slot
    extra = 2

class ParentRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "parent"
    raw_id_fields = ("create_user", 'child')



class ChildtRelationshipInLIne(admin.TabularInline):
    model = Relationship
    extra = 1
    fk_name = "child"
    raw_id_fields = ("create_user", 'parent')

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
    raw_id_fields = ("create_user", 'attr')


class ItemAdmin(admin.ModelAdmin):
    inlines = [ParentRelationshipInLIne, ChildtRelationshipInLIne, ValuesInline ]
    raw_id_fields = ("create_user", 'update_user', 'community')




admin.site.register(User, TPPUserAdmin)
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
admin.site.register(Slot)
#admin.site.register(AttrTemplate)
