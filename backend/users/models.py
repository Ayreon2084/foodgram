from common.constants import LENGTH_150, LENGTH_254
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
        verbose_name='Avatar',
        upload_to='users/',
        null=True,
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'user'
        verbose_name_plural = 'Users'

    def __str__(self):
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
        verbose_name='Subscriber',
        related_name='follower',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'follow'
        verbose_name_plural = 'Follows'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='prevent_double_follow'
            ),
        ]

    def __str__(self):
        return f'User {self.user} follows {self.author}.'
