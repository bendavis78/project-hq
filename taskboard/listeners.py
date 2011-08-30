from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from . import models

@receiver(post_save, sender=models.Task)
def update_task_sprints(sender, **kwargs):
    cache.delete('task_sprints')
