from django.db import models

NAME_LENGHT = 128
MEANSUREMENT_LENGHT = 64


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=NAME_LENGHT,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MEANSUREMENT_LENGHT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
