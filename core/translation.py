from modeltranslation.translator import translator, TranslationOptions
from core.models import Attribute, Item, Slot, Value

class AttributeTranslationOptions(TranslationOptions):
    fields = ('title',)

class ItemTranslationOptions(TranslationOptions):
    fields = ('title',)

class SlotTranslationOptions(TranslationOptions):
    fields = ('title',)

class ValueTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(Attribute, AttributeTranslationOptions)
translator.register(Item, ItemTranslationOptions)
translator.register(Slot, SlotTranslationOptions)
translator.register(Value, ValueTranslationOptions)