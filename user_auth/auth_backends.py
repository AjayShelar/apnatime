from user_auth.models import User


class UsernameBackend(object):
    """
    authenticating using username

    """

    def authenticate(self, username=None, password=None, **kwargs):

        try:
            print(kwargs.get('username'))

            user = User.objects.get(
                username=username)

            if not user.is_active:
                user.is_active = True
                user.save()

            return user

        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class PhoneNumberBackend(object):
    """
    authenticating using phone_number
    """

    def authenticate(self, username=None, password=None, **kwargs):

        try:
            print(kwargs.get('phone_number'))
            user = User.objects.get(
                phone_number=kwargs.get('phone_number'))

            if not user.is_active:
                user.is_active = True
                user.save()

            return user

        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
