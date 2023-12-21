from django.db import models

MAX_LENGTH_NAME = 200


class AbstractModel(models.Model):
    """Абстрактная модель."""
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME
    )

    class Meta:
        abstract = True
