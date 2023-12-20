from django.db import models


class AbstractModel(models.Model):
    """Абстрактная модель."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )

    class Meta:
        abstract = True
