from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone
from datetime import datetime, timedelta
from amon.utils.generators import random_id_generator

class AmonUserManager(BaseUserManager):
    def create_user(self, email=None, password=None):
        """
        Creates and saves a User with the given email, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_active = True
        user.save()
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.save()


class AmonUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    organizations = models.ManyToManyField('organizations.Organization')

    USERNAME_FIELD = 'email'

    objects = AmonUserManager()

    def get_short_name(self):
        return self.email

    def get_username(self):
        return self.email

    def __str__(self):
        return "Email: {0}".format(self.email)

    class Meta:
        verbose_name = 'User'



class ResetPasswordCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_password_reset_code',
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=128)
    expires_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    date_created = models.DateTimeField(('date created'), default=timezone.now)


    @staticmethod
    def generate_password_reset_token(user):
        activation_code = ResetPasswordCode.objects.create(
            user=user,
            code=random_id_generator(size=64),
            expires_on=datetime.utcnow() + timedelta(days=1)
        )

        return activation_code

    def __str__(self):
        return "Email: {0} / Code: {1}".format(self.user.email, self.code)