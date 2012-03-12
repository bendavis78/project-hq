from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from taskboard import settings
from . import models

@receiver(post_save, sender=models.Task)
def update_task_iterations(sender, **kwargs):
    cache.delete(settings.ITERATION_CACHE_KEY)
