from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions

from jobs.models import Requirement, Resume


@register(Requirement)
class RequirementTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'city', 'description', 'requirements', 'terms', 'keywords', )


@register(Resume)
class ResumeTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'nationality', 'address', 'faculty', 'profession', 'study_form', 'company_exp_1',
              'company_exp_2', 'company_exp_3', 'position_exp_1', 'position_exp_2', 'position_exp_3',
              'additional_study', 'language_skill', 'computer_skill', 'additional_skill', 'additional_information',
              'institution')
