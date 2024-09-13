from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from common.constants import LENGTH_150, LENGTH_254


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=LENGTH_254
    )
    username = models.CharField(
        verbose_name='Username',
        unique=True,
        max_length=LENGTH_150,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                message=(
                    'Username must contain only alphanumeric characters, '
                    'dots, pluses, ats, and hyphens.'
                )
            )
        ],
    )
    first_name = models.CharField(
        verbose_name='Name',
        max_length=LENGTH_150
    )
    last_name = models.CharField(
        verbose_name='Surname',
        max_length=LENGTH_150
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        blank=True,
        default='users/default_avatar.png',
        verbose_name='Avatar'
    )
    # # To be used for superuser creation
    # REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'user'
        verbose_name_plural = 'Users'

    def __sta__(self):
        return f'User: {self.username}.'


class FollowUser(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Recipe author',
        related_name='followed',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Subscriber'
    )

    class Meta:
        verbose_name = 'follow'
        verbose_name_plural = 'Follows'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='prevent_double_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'User {self.user} follows {self.author}.'