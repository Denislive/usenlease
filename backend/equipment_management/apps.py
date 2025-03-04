from django.apps import AppConfig
from django.db.models.signals import post_migrate

def setup_periodic_tasks(sender, **kwargs):
    from .tasks import setup_periodic_task, setup_periodic_task_reduce_equipment
    setup_periodic_task()
    setup_periodic_task_reduce_equipment()

class EquipmentManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "equipment_management"

    def ready(self):
        post_migrate.connect(setup_periodic_tasks, sender=self)
