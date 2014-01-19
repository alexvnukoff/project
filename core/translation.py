from modeltranslation.translator import translator, TranslationOptions
from core.models import Slot, Value

class SlotTranslationOptions(TranslationOptions):
    fields = ('title',)

class ValueTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(Value, ValueTranslationOptions)

translator.register(Slot, SlotTranslationOptions)
