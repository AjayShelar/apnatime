from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, UserManager
from apnatime.settings import LANGUAGES

# Create your models here.


class CustomUserManager(UserManager):
    def create_superuser(self, username, phone_number, password, **kwargs):
        extra_fields = {'is_active': True, 'phone_number': phone_number}
        return super(CustomUserManager, self).create_superuser(username, None, password,
                                                               **extra_fields)


class User(AbstractUser):
    phone_number = PhoneNumberField(unique=True)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'User', blank=True, null=True, related_name='created_users', on_delete=models.CASCADE)
    edited_by = models.ForeignKey(
        'User', blank=True, null=True,  on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ('phone_number', )
    objects = CustomUserManager()

    @staticmethod
    def create_user(**kwargs):
        user = User(**kwargs)
        user.clean()
        user.save()
        return user

    def clean(self):
        if not self.username:
            # Set username as phone number
            self.username = str(self.phone_number)

        if not self.password:
            self.set_unusable_password()

    @property
    def name_prop(self):
        return self.name()

    @property
    def language_prop(self):
        return self.language_code()

    def language_code(self):
        try:
            return self.profile.language.split('-')[0]
        except Exception as e:
            return 'en'

    def name(self):
        return str(self.first_name + " " + self.last_name).strip()

    def photo(self):
        try:
            return self.profile.photo.url
        except Exception as e:
            return None

    def __str__(self):
        return str(self.name() or self.phone_number.__str__())


def content_file_name(instance, filename):
    return "user" + str(instance.user.pk)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    photo = models.ImageField(
        upload_to=content_file_name, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    language = models.CharField(
        max_length=255, default='en-US', choices=LANGUAGES)

    def __str__(self):
        return str(self.user.name())
