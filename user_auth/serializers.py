from rest_framework import serializers

from .models import *

from phonenumber_field.serializerfields import PhoneNumberField
from apnatime.settings import LANGUAGES


class UserProfileSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(
        required=True, choices=LANGUAGES)

    class Meta(object):
        model = UserProfile
        fields = ('photo', 'language', 'birthdate',
                  'years_of_experience', 'address')


class UserDataSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField(required=True)

    photo = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'phone_number',  'photo',  'first_name', 'last_name', 'id', 'is_staff',
            'is_active', 'profile',
        ]

    def create(self, validated_data):
        # print("----------in")
        if validated_data.get('type', None):
            user = User(
                phone_number=validated_data['phone_number'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )
        else:
            user = User(
                phone_number=validated_data['phone_number'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )

        user.clean()
        user.save()
        profile, created = UserProfile.objects.get_or_create(user=user)
        if 'profile' in validated_data:
            profile.language = validated_data['profile']['language']

        profile.save()

        # Create profile

        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.clean()
        instance.save()

        # Create profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if 'profile' in validated_data:
            profile.language = validated_data['profile']['language']
        profile.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'password')


class RegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = UserProfile
        fields = ('language', 'user', 'birthdate', 'address')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.create_user(**user_data)

        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile


from django.contrib.auth import authenticate
from django.core import exceptions


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        print(username)
        print(password)
        print(phone_number)

        user = authenticate(
            username=username, password=password, phone_number=phone_number)
        print(user)
        if user:
            if not user.is_active:
                msg = 'User account is disabled.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Unable to log in with provided credentials.'
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


from rest_auth.models import TokenModel

from rest_auth.serializers import TokenSerializer


class CustomTokenSerializer(TokenSerializer):
    """
    Serializer for Token authentication.
    Just to override rest_auth default UserDetailsSerializer.
    Used during login.
    """
    user = UserSerializer()

    class Meta(object):
        model = TokenModel
        fields = ['key', 'user']
