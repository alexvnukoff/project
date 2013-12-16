from core.models import (Action, ActionPath, Attribute, Identity, Item, Participant, Permission, Relationship,
                         Dictionary, State, Slot, Process)
from django.contrib import admin

admin.site.register(Action)
admin.site.register(ActionPath)
admin.site.register(Attribute)
admin.site.register(Identity)
admin.site.register(Item)
admin.site.register(Participant)
admin.site.register(Process)
admin.site.register(Permission)
admin.site.register(Relationship)
admin.site.register(Dictionary)
admin.site.register(State)
admin.site.register(Slot)