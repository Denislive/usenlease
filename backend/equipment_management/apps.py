from django.apps import AppConfig

class EquipmentManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "equipment_management"

    def ready(self):
        from .tasks import setup_periodic_task, setup_periodic_task_reduce_equipment
        setup_periodic_task()
        setup_periodic_task_reduce_equipment()
