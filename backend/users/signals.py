import os

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Delete image file with avatar if user is being deleted."""
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            instance.avatar.delete(save=False)


@receiver(pre_save, sender=User)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """
    Delete image file with avatar.

    Cases:
    - user deletes current avatar;
    - user changes current avatar.
    """
    if not instance.pk:
        return

    if User.objects.filter(pk=instance.pk).exists():
        old_avatar = User.objects.get(pk=instance.pk).avatar
        new_avatar = instance.avatar

        if (
            old_avatar
            and old_avatar != new_avatar
            and os.path.isfile(old_avatar.path)
        ):
            old_avatar.delete(save=False)
