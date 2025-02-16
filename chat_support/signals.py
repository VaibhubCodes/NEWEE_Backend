from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import Count
from .models import SupportTicket
from users.models import CustomUser  # Assuming CustomUser model exists in users app

@receiver(pre_save, sender=SupportTicket)
def escalate_overdue_tickets(sender, instance, **kwargs):
    """
    Automatically escalates a ticket if the due date has passed.
    """
    if instance.status in ["open", "in_progress"] and instance.due_date and instance.due_date < now():
        instance.priority = "critical"  # Auto-escalate overdue tickets to 'critical'
        print(f"🚨 Ticket {instance.ticket_id} auto-escalated due to overdue!")

@receiver(post_save, sender=SupportTicket)
def notify_ticket_comment(sender, instance, created, **kwargs):
    """
    Sends a notification when a new comment is added to a ticket.
    - If the comment is public, notify both Student & Controller.
    - If the comment is internal, notify only the Controller.
    """
    if not created and "comments" in instance.__dict__:
        last_comment = instance.comments[-1] if instance.comments else None

        if last_comment:
            author_name = last_comment.get("author_name")
            visibility = last_comment.get("visibility")

            # Determine recipients
            recipients = [instance.assigned_controller] if visibility == "internal" else [instance.assigned_controller, instance.student]
            recipients = [user for user in recipients if user is not None]  # Remove None values

            # Print Notifications (Replace with real notification system)
            for recipient in recipients:
                print(f"🔔 Notification: New comment on Ticket {instance.ticket_id} by {author_name}. Visible to {visibility}.")

