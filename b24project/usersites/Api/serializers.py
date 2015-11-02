from rest_framework import serializers
from centerpokupok.models import B2CProductCategory


class B2CProductCategorySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        pass

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = B2CProductCategory
