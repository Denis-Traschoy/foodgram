from django.db import models

SLUG_LENGHT = 32


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=SLUG_LENGHT,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_LENGHT,
        unique=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name
