from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        null=True,
    )
    text = models.TextField(
        'Текст',
        help_text='Введите текст'
    )

    class Meta:
        abstract = True
