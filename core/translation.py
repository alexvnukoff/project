from modeltranslation.translator import translator, TranslationOptions
from core.models import Attribute, Item, Slot, Value

class AttributeTranslationOptions(TranslationOptions):
    fields = ('title',)



class SlotTranslationOptions(TranslationOptions):
    fields = ('title',)

class ValueTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(Attribute, AttributeTranslationOptions)

translator.register(Slot, SlotTranslationOptions)
