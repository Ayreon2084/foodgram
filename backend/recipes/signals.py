import logging
import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Recipe

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Recipe)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Delete file with recipe image if recipe is being deleted."""
    logger.info(f'Deleting image for recipe: {instance.name}')
    if instance.image:
        if os.path.isfile(instance.image.path):
            logger.info(f'Removing file at: {instance.image.path}')
            instance.image.delete(save=False)


@receiver(pre_save, sender=Recipe)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """
    Delete file with recipe image.

    Cases:
    - current recipe image is being deleted;
    - current recipe image is being changed.
    """
    if not instance.pk:
        return

    if Recipe.objects.filter(pk=instance.pk).exists():
        old_image = Recipe.objects.get(pk=instance.pk).image
        new_image = instance.image

        if (
            old_image
            and old_image != new_image
            and os.path.isfile(old_image.path)
        ):

            old_image.delete(save=False)
