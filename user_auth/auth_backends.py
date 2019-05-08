from user_auth.models import User


class Backend(object):
    """
    Custom authentication backend to authenticate with
    """

    def authenticate(self, username=None, password=None, **kwargs):
        print(kwargs.get('phone_number', username))
        print(User.objects.all())
        print(User.objects.get(
            phone_number=kwargs.get('phone_number')))
        print([u.phone_number for u in User.objects.all()])
        try:
            # Fallback to username for login to allow logging in even using username
            user = User.objects.get(
                phone_number=kwargs.get('phone_number'))
            # Login with OTP

            if not user.is_active:
                user.is_active = True
                user.save()

            return user

        except User.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
