from django.db.models.signals import post_save
from django.dispatch import receiver
from taskboard.utils import clear_iteration_cache
from . import models

@receiver(post_save, sender=models.Task)
def update_task_iterations(sender, **kwargs):
    clear_iteration_cache()
    models.Task.orderable.clean_ordering()
