from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils import timezone

from base.models import UpdatedAtModel


class UserManager(BaseUserManager):
    def delete_unverified_users(self):
        print("deleting unverified users")
        self.filter(is_verified=False, date_joined__lte=timezone.now() - timedelta(days=2)).update(is_active=False)


class User(AbstractUser, UpdatedAtModel):
    """Пользователь."""

    is_verified = models.BooleanField(default=False, verbose_name="Верифицированный?")

    objects = UserManager()

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"
