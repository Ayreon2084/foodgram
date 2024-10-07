from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from common.constants import LENGTH_150, LENGTH_254, USERNAME_REGEX


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='Эл. почта',
        unique=True,
        max_length=LENGTH_254
    )
    username = models.CharField(
        verbose_name='Логин',
        unique=True,
        max_length=LENGTH_150,
        validators=[
            RegexValidator(
                USERNAME_REGEX,
                message=(
                    'Username must contain only alphanumeric characters, '
                    'dots, pluses, ats, and hyphens.'
                )
            )
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LENGTH_150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGTH_150
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        null=True,
        blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'Пользователь: "{self.username}".'


class FollowUser(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='followed',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'подписка на пользователей'
        verbose_name_plural = 'Подписки на пользователей'
        ordering = ('author', 'user')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='prevent_double_follow'
            )
        ]

    def __str__(self):
        return f'Ползователь "{self.user}" подписан на "{self.author}".'
