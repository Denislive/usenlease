from celery import shared_task
from django.utils.timezone import now
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from .models import OrderItem

@shared_task
def reject_expired_orders():
    """
    Automatically reject orders whose start_date has passed.
    """
    today = now().date()
    expired_orders = OrderItem.objects.filter(status='pending', start_date__lt=today)
    for order_item in expired_orders:
        order_item.status = 'rejected'
        order_item.save()
    return f"Rejected {expired_orders.count()} expired orders."

@shared_task
def reduce_equipment_available():
    """
    For order items with status 'rented' that start today,
    reduce the available equipment quantity by the order item quantity.
    """
    today = now().date()
    order_items = OrderItem.objects.filter(status='pending', start_date=today)
    count = 0
    for order_item in order_items:
        equipment = order_item.item  # Assuming 'item' is a FK to Equipment.
        # Adjust the available quantity field as per your Equipment model.
        equipment.available_quantity = equipment.available_quantity - order_item.quantity
        equipment.save()
        count += 1
    return f"Reduced equipment availability for {count} order items."

# Register the periodic task for rejecting expired orders
def setup_periodic_task():
    """
    Ensures the periodic task for rejecting expired orders is created or updated.
    """
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=0,      # At minute 00
        hour=21,       # At 21:00 UTC (adjust based on your timezone settings)
        day_of_week="*",
        day_of_month="*",
        month_of_year="*"
    )

    task, created = PeriodicTask.objects.update_or_create(
        name="Reject expired orders",
        defaults={
            "crontab": schedule,
            "task": "equipment_management.tasks.reject_expired_orders",
            "args": json.dumps([]),
        },
    )

    if created:
        print("✅ Periodic Task Created: Reject expired orders")
    else:
        print("🔄 Periodic Task Updated: Reject expired orders")

# Register the periodic task for reducing equipment availability
def setup_periodic_task_reduce_equipment():
    """
    Ensures the periodic task for reducing equipment availability is created or updated.
    """
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=0,      # At minute 00
        hour=21,       # Same schedule as reject_expired_orders; adjust if needed.
        day_of_week="*",
        day_of_month="*",
        month_of_year="*"
    )

    task, created = PeriodicTask.objects.update_or_create(
        name="Reduce equipment available",
        defaults={
            "crontab": schedule,
            "task": "equipment_management.tasks.reduce_equipment_available",
            "args": json.dumps([]),
        },
    )

    if created:
        print("✅ Periodic Task Created: Reduce equipment available")
    else:
        print("🔄 Periodic Task Updated: Reduce equipment available")
