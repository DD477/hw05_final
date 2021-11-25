import textwrap as tw

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        help_text='Выберите группу',
        max_length=200
    )
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(CreatedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',

    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='groups',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return tw.shorten(self.text, 15, placeholder='...')


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Пост',
        related_name='comments',

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )

    def __str__(self):
        return tw.shorten(self.text, 15, placeholder='...')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

# Не понял как проверить тут подписку на самого себя
    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return (f'Пользователь {self.user} подписан '
                f'на пользователя {self.author}')
