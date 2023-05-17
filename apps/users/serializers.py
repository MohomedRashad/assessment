import django.db.utils
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.error_codes import AccountErrorCodes
from apps.users.models import Doctor, Patient, Pharmacy, Roles
from project import settings

def create_user(validated_data):
    if validated_data.get('role') == Roles.PHARMACY and not all([validated_data.get('pharmacy_name'), validated_data.get('postal_code')]):
        raise ValidationError('Please provide pharmacy name and postal code for pharmacy users')

    validated_data.pop('confirm_password')
    validated_data['username'] = validated_data['email']
    instance = get_user_model().objects.create(
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        username=validated_data['email'],
        role=validated_data['role']
    )
    instance.set_password(validated_data['password'])
    instance.save()

    if validated_data['role'] == Roles.PHARMACY:
        Pharmacy.objects.create(user=instance, name=validated_data['pharmacy_name'], postal_code=validated_data['postal_code'])
    elif validated_data['role'] == Roles.DOCTOR:
        Doctor.objects.create(user=instance, speciality=validated_data['speciality'], license_number=validated_data['license_number'], years_of_experience=validated_data['years_of_experience'], bio=validated_data['bio'])
    elif validated_data['role'] == Roles.PATIENT:
        Patient.objects.create(user=instance, height=validated_data['height'], weight=validated_data['weight'], date_of_birth=validated_data['date_of_birth'], medical_history=validated_data['medical_history'])

    return instance

class AuthRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True, min_length=6)
    pharmacy_name = serializers.CharField(required=False)
    postal_code = serializers.CharField(required=False)
    speciality = serializers.CharField(required=False)
    license_number = serializers.CharField(required=False)
    years_of_experience = serializers.IntegerField(required=False)
    bio = serializers.CharField(required=False)
    height = serializers.FloatField(required=False)
    weight = serializers.FloatField(required=False)
    date_of_birth = serializers.DateField(required=False)
    medical_history = serializers.CharField(required=False)
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'role', 'pharmacy_name', 'postal_code', 'speciality', 'license_number', 'years_of_experience', 'bio', 'height', 'weight', 'date_of_birth', 'medical_history']
        extra_kwargs = {
            'id': {'read_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'min_length': 6},
            'role': {'required': True},
            'pharmacy_name': {'required': False},
            'postal_code': {'required': False},
            'speciality': {'required': False},
            'license_number': {'required': False},
            'years_of_experience': {'required': False},
            'bio': {'required': False},
            'height': {'required': False},
            'weight': {'required': False},
            'date_of_birth': {'required': False},
            'medical_history': {'required': False},
        }

    def validate_confirm_password(self, val):
        password = self.initial_data['password']
        if val != password:
            raise ValidationError(AccountErrorCodes.PASSWORD_MISMATCH)

    @transaction.atomic
    def create(self, validated_data):
        try:
            user = create_user(validated_data)
            if settings.VERIFY_EMAIL:
                user.is_active = False
                user.save()
                user.generate_email_verification_code()
            return user
        except django.db.utils.IntegrityError:
            # todo: Add logger to log the exception
            raise ValidationError(AccountErrorCodes.USER_EXIST)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'id': {'read_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'read_only': True},
            'role': {'read_only': True},
        }

class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_new_password = serializers.CharField(required=True, min_length=6)

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password', 'confirm_new_password']

    def validate_confirm_new_password(self, val):
        password = self.initial_data['new_password']
        if val != password:
            raise ValidationError(AccountErrorCodes.PASSWORD_MISMATCH)

    def update(self, instance, validated_data):
        if instance.check_password(validated_data['old_password']):
            instance.set_password(validated_data['new_password'])
            return instance
        else:
            raise ValidationError(AccountErrorCodes.INVALID_PASSWORD)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'id': {'read_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'read_only': True},
            'role': {'read_only': True},
        }

class UserRequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_new_password = serializers.CharField(required=True, min_length=6)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.user = get_object_or_404(get_user_model(), email=self.initial_data['email'])
        except Http404:
            raise ValidationError(AccountErrorCodes.UNKNOWN_USER)

    def validate_confirm_new_password(self, val):
        password = self.initial_data['new_password']
        if val != password:
            raise ValidationError(AccountErrorCodes.PASSWORD_MISMATCH)

    def validate_token(self, val):
        if not default_token_generator.check_token(self.user, val):
            raise ValidationError(AccountErrorCodes.UNKNOWN_USER)

    class Meta:
        model = get_user_model()
        fields = ['new_password', 'confirm_new_password', 'token', 'email']
