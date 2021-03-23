from crypt import (
    METHOD_SHA256,
    crypt,
)
from hmac import compare_digest as compare_hash

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse

from .common import username_validator
from .domain import MailDomain


class MailUserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, email):
        if '@' in email:
            name, domain_name = email.split('@', 1)
            return MailUser.objects.get(name=name, domain__name=domain_name)
        else:
            return MailUser.objects.get(name=email, domain__isnull=True)

    def create_user(self, name, domain_name, password=None):
        if not name or not domain_name:
            raise ValueError("You should provide both name and domain_name")
        domain = MailDomain.objects.get_or_create(name=domain_name)
        user = self.model(name=name, domain=domain)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, name, password=None):
        if not name:
            raise ValueError("The name should be filled with a simple username")
        user = self.model(name=name, domain=None, is_superuser=True)
        user.set_password(password)
        user.save()
        return user


class MailUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, validators=[username_validator])
    password = models.CharField(max_length=255, help_text="encrypted password")
    is_superuser = models.BooleanField(default=False, db_column='superadmin', help_text="admin for all domains")
    domain = models.ForeignKey('MailDomain', on_delete=models.CASCADE, related_name="users",
                               null=True, blank=True,
                               help_text="Could be null for the superadmin")
    is_admin = models.BooleanField(default=False, db_column='admin', help_text="admin for its domain")
    is_active = models.BooleanField(default=True, db_column='enabled')
    send_only = models.BooleanField(default=False)
    quota = models.PositiveIntegerField(default=0, help_text="0 means no quota, size is in MB")

    # those constants are used for createsuperuser command
    objects = MailUserManager()
    USERNAME_FIELD = 'name'
    PASSWORD_FIELD = 'password'
    REQUIRED_FIELDS = []

    @property
    def email(self):
        return f"{self.name}@{self.domain}" if self.domain else self.name

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_domain_admin(self):
        return self.is_superuser or self.is_admin

    def clean(self):
        self.name = self.normalize_username(self.name)

    def get_username(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def set_password(self, raw_password):
        if raw_password:
            # default to 5000 rounds for SHA256
            self.password = crypt(raw_password, salt=METHOD_SHA256)

    def check_password(self, raw_password):
        return compare_hash(crypt(raw_password, self.password), self.password)

    def set_unusable_password(self):
        self.password = '*'

    def has_usable_password(self):
        return self.password and not self.password.startswith('*')

    def __str__(self):
        return (
            f"{self.get_full_name()} ({self.is_active})"
            f" S:{self.is_superuser} A:{self.is_domain_admin} SO:{self.send_only}"
        )

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'mail_users'
        ordering = ['name', 'domain__name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'domain'], name='user_idx'),
        ]
