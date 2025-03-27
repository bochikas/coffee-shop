import logging

from django.db import models
from django.utils.functional import classproperty

from base.fields import UUIDField

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    """Base model for all models."""

    id = UUIDField(primary_key=True, version=7)

    class Meta:
        abstract = True

    @classproperty
    def app_label(cls):  # noqa
        return cls._meta.app_label  # noqa

    @classproperty
    def model_name(cls):  # noqa
        return cls._meta.model_name  # noqa

    @classmethod
    def get_field(cls, field_name):
        return cls._meta.get_field(field_name)


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class IsActiveModel(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="Активно?")

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True


class CreatedAtModel(BaseModel):
    created_at = models.DateTimeField(verbose_name="Создано", auto_now_add=True, blank=True)

    class Meta:
        abstract = True


class TitleModel(BaseModel):
    title = models.CharField(max_length=255, verbose_name="название")

    class Meta:
        abstract = True


class UpdatedAtModel(BaseModel):
    updated_at = models.DateTimeField("Обновлено", auto_now=True, blank=True)

    class Meta:
        abstract = True


class TimeStampedModel(CreatedAtModel, UpdatedAtModel):
    class Meta:
        abstract = True


class IsActiveTitleTimeStampedModel(IsActiveModel, CreatedAtModel, UpdatedAtModel, TitleModel):
    class Meta:
        abstract = True
