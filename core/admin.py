from core.models import (Action, ActionPath, Attribute, Client, Item, Relationship,
                         Dictionary, State, Slot, Process, Value)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'client'

class UserAdmin(UserAdmin):
    inline = (ClientInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Action)
admin.site.register(ActionPath)
admin.site.register(Attribute)
admin.site.register(Client)
admin.site.register(Item)
admin.site.register(Process)
admin.site.register(Relationship)
admin.site.register(Dictionary)
admin.site.register(State)
admin.site.register(Slot)
admin.site.register(Value)