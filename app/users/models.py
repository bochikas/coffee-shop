from base.models import UpdatedAtModel
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(UpdatedAtModel, AbstractUser):
    """Пользователь."""

    is_verified = models.BooleanField(default=True, verbose_name="Верифицированный?")

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"
