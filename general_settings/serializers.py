from rest_framework import serializers

from utils.image_formatter import get_formatted_image
from .models import GeneralSettings


class GeneralSettingsSerializer(serializers.ModelSerializer):
    company_logo = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=True)
    company_logo_url = serializers.ImageField(read_only=True, source='company_logo')

    class Meta:
        model = GeneralSettings
        fields = '__all__'

    def update(self, instance, validated_data):
        company_logo = validated_data.pop('company_logo', None)
        instance = super().update(instance, validated_data)
        if company_logo == 'delete':
            instance.company_logo = None
        elif company_logo:
            instance.company_logo = get_formatted_image('company_logo', company_logo)
        instance.save()
        return instance


class SetupPagesSerializer(serializers.Serializer):
    page_url_customer_login = serializers.URLField(allow_blank=True)
    page_url_customer_dashboard = serializers.URLField(allow_blank=True)
    terms_and_policies = serializers.URLField(allow_blank=True)
    page_url_customer_waiver_submission = serializers.URLField(allow_blank=True, allow_null=True)
    referral_page_url = serializers.URLField(allow_blank=True, allow_null=True)


class BusinessInformationSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=100)
    business_phone = serializers.CharField(max_length=20)
    business_address = serializers.CharField(max_length=255)


class PhoneSettingsSerializer(serializers.Serializer):
    show_phone_countries = serializers.CharField(max_length=255)
    default_phone_country = serializers.CharField(max_length=255)
    included_phone_countries = serializers.ListField(child=serializers.CharField(max_length=50))
    validate_phone_number = serializers.BooleanField()
    format_phone_number = serializers.BooleanField()
    show_dial_code_with_flag = serializers.BooleanField()


class AppGeneralSettingsSerializer(serializers.ModelSerializer):
    phone = PhoneSettingsSerializer()
    setup_pages = SetupPagesSerializer()
    company_logo = serializers.ImageField(required=False, allow_null=True)
    business_information = BusinessInformationSerializer()

    class Meta:
        model = GeneralSettings
        fields = [
            'id', 'phone', 'setup_pages', 'company_logo', 'business_information'
        ]


class TestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    send_type = serializers.ChoiceField(choices=[('direct', 'Direct'), ('celery', 'Celery')])
