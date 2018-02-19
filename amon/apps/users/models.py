from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone


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

