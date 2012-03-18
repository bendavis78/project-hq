from django.db.models.signals import post_save
from django.dispatch import receiver
from taskboard.utils import clear_iteration_cache
from . import models

iteration_changing_models = (
    models.Task,
    models.Team,
    models.TeamStrengthAdjustment,
)

@receiver(post_save)
def update_task_iterations(sender, **kwargs):
    if sender in iteration_changing_models:
        clear_iteration_cache()
        models.Task.orderable.clean_ordering()
