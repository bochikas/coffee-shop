from django.contrib.auth.models import AbstractUser
from django.db import models

from base.models import UpdatedAtModel


class User(AbstractUser, UpdatedAtModel):
    """Пользователь."""

    is_verified = models.BooleanField(default=False, verbose_name="Верифицированный?")

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"
