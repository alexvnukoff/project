# -*- encoding: utf-8 -*-

import logging

from django.db import transaction, IntegrityError
from django.utils.text import Truncator
from lxml.html.clean import clean_html
from rest_framework import serializers

from b24online.models import (Questionnaire, Question, QuestionnaireCase,
                              Recommendation, QuestionnaireParticipant,
                              Answer)

from appl.func import currency_symbol

logger = logging.getLogger(__name__)


class ListAdditionalPageSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):

        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
        }

class DetailAdditionalPageSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'fullText': clean_html(obj.content) if obj.content else '',
        }

class ListNewsSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):

        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.content).words("30", html=True)

        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'cover': obj.image.big if obj.image else '',
            'shortText': clean_html(short_text) if short_text else '',
        }


class DetailNewsSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'cover': obj.image.big if obj.image else '',
            'fullText': clean_html(obj.content) if obj.content else '',
        }


class ListBusinessProposalSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'shortText': clean_html(Truncator(obj.description).words("30", html=True)) if obj.description else '',
        }


class DetailBusinessProposalSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'title': clean_html(obj.title),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'fullText': clean_html(obj.description) if obj.description else '',
        }


class GallerySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'url': obj.image.original,
            'description': '',
        }


class DepartmentSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'unit': clean_html(obj.name),
            'workers': VacancySerializer(obj.vacancies.all(), many=True).data,
        }


class VacancySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'img': obj.user.profile.avatar.th if obj.user and obj.user.profile.avatar else '',
            'name': clean_html(obj.user.profile.full_name) if obj.user and obj.user.profile.full_name else '',
            'post': clean_html(obj.name) if obj.name else '',
            'phone': clean_html(obj.user.profile.mobile_number) if obj.user and obj.user.profile.mobile_number else ''
        }


class ListB2BProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.description).words("30", html=True)

        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(short_text) if short_text else ''
        }


class DetaiB2BlProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(obj.description) if obj.description else ''
        }


class ListB2CProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.description).words("30", html=True)

        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(short_text) if short_text else ''
        }


class DetaiB2ClProductSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'pubDate': obj.created_at.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'price': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(obj.description) if obj.description else ''
        }


class B2CProductCategorySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'parentId': obj.parent_id,
        }


class B2BProductCategorySerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'parentId': obj.parent_id,
        }


class ListCouponSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        if obj.short_description:
            short_text = obj.short_description
        else:
            short_text = Truncator(obj.description).words("30", html=True)

        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'endDate': obj.end_coupon_date.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'oldPrice': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(short_text) if short_text else '',
            'percent': obj.coupon_discount_percent
        }


class DetaiCouponSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'name': clean_html(obj.name),
            'endDate': obj.end_coupon_date.strftime("%d.%m.%y"),
            'currency': currency_symbol(obj.currency),
            'oldPrice': obj.cost,
            'cover': obj.image.big if obj.image else '',
            'details': clean_html(obj.description) if obj.description else '',
            'percent': obj.coupon_discount_percent
        }


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Serializer for Questionnaire model.
    """
    
    image = serializers.SerializerMethodField('get_image_original', 
                                              read_only=True)
    item_cost = serializers.FloatField(source='item.cost', read_only=True)

    def __new__(cls, *args, **kwargs):
        if kwargs.get('many', False):
            pass
        return super(QuestionnaireSerializer, cls)\
            .__new__(cls, *args, **kwargs)
                                                
    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'short_description', 'image', 'item_cost', 
                  'use_show_result')

    def get_image_original(self, instance):
        return instance.image.original if instance.image else None


class CaseQuestionAnswerSerializer(serializers.Serializer):
    """
    Question's answer serializer.
    """
    question_id = serializers.IntegerField(required=True)
    answer = serializers.BooleanField(required=True)
    show_answer = serializers.BooleanField(required=False)
    

class CaseExtraQuestionAnswerSerializer(serializers.Serializer):
    """
    Extra question's answer serializer.
    """
    question_text = serializers.CharField(required=True)
    answer = serializers.BooleanField(required=True)
    show_answer = serializers.BooleanField(required=False)
    

class AtFirstCaseAnswersSeializer(serializers.Serializer):
    """
    Process data for inviter answers.
    """
    questionnaire_id = serializers.IntegerField(required=True)
    inviter_email = serializers.EmailField(required=True)
    invited_email = serializers.EmailField(required=True)
    answers = CaseQuestionAnswerSerializer(many=True)
    extra_answers = CaseExtraQuestionAnswerSerializer(
        many=True, 
        required=False
    )

    def save(self):
        inviter_participant = None
        instance = None
        try:
            try:
                questionnaire = Questionnaire.objects.get(
                    id=self.validated_data['questionnaire_id']
                )
            except Questionnaire.DoesNotExist:
                raise IntergityError
                
            with transaction.atomic():
                instance = QuestionnaireCase.objects.create(
                    questionnaire=questionnaire,
                    status=QuestionnaireCase.DRAFT,
                )
                invited_email = self.validated_data.get('invited_email')
                if invited_email:
                    invited_participant = QuestionnaireParticipant.objects\
                        .create(
                            email=invited_email,
                            is_invited=True
                        )
                    instance.participants.add(invited_participant)
                    inviter_email = self.validated_data.get('inviter_email')
                if inviter_email:
                    inviter_participant = QuestionnaireParticipant(
                        email=inviter_email,
                        is_invited=False,
                    )
                    inviter_participant.save()
                    instance.participants.add(inviter_participant)
                    responsive = inviter_participant

                for answer_data in self.validated_data['answers']:
                    question_id = int(answer_data['question_id'])
                    try:
                        question = Question.objects.get(
                            id=question_id
                        )
                    except Question.DoesNotExist:
                        continue    
                    answer_value = answer_data.get('answer', False)
                    if questionnaire.use_show_result:
                        new_answer = Answer.objects.create(
                            questionnaire_case=instance,
                            question=question,
                            participant=responsive,
                            answer=answer_value,
                            show_answer=answer_data.get('show', False),
                        )
                    else:
                        if answer_value:
                            new_answer = Answer.objects.create(
                                questionnaire_case=instance,
                                question=question,
                                participant=responsive,
                                answer=True,
                            )

        except IntegrityError:
            return None
        else:
            return instance
        

class ListQuestionSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'question_text': obj.question_text,
        }
        