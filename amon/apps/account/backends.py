from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend(ModelBackend):

    def authenticate(self, email=None, password=None, **kwargs):
        if email and password:
            try:
                user = User.objects.get(email__iexact=email)
                if user.check_password(password):
                    return user
                return None
            except User.DoesNotExist:
                return None

        return None
