import uuid
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import Count
from datetime import timedelta

User = settings.AUTH_USER_MODEL

# Ticket Priority Choices
TICKET_PRIORITIES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
]

# Ticket Status Choices
TICKET_STATUSES = [
    ("open", "Open"),
    ("in_progress", "In Progress"),
    ("resolved", "Resolved"),
    ("closed", "Closed"),
]

# Ticket Categories
TICKET_CATEGORIES = [
    ("finance", "Finance Issue"),
    ("educator", "Doubt / Educator Issue"),
    ("tech", "Technical Issue"),
    ("quiz", "Quiz Issue"),
    ("product", "Product Delivery Issue"),
    ("master", "All Types / Complex Issue"),
]

# Comment Visibility
COMMENT_VISIBILITY_CHOICES = [
    ("public", "Public"),  # Visible to Student & Controller
    ("internal", "Internal"),  # Visible only to Controllers/Admins
]

class SupportTicket(models.Model):
    SLA_TIMEFRAMES = {
        "low": 72,  # 3 days
        "medium": 48,  # 2 days
        "high": 24,  # 1 day
        "critical": 12,  # 12 hours
    }

    ticket_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    assigned_controller = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets"
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=TICKET_CATEGORIES, default="tech")  # ✅ Added category
    priority = models.CharField(max_length=10, choices=TICKET_PRIORITIES, default="low")
    status = models.CharField(max_length=20, choices=TICKET_STATUSES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)  # ✅ Added due date field
    comments = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        """Automatically calculate `due_date` based on priority level and auto-assign controller."""
        if not self.due_date or "priority" in kwargs:
            self.due_date = now() + timedelta(hours=self.SLA_TIMEFRAMES.get(self.priority, 48))
        
        if self.status == "in_progress" and not self.assigned_controller:
            self.assign_controller()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.status}"

    def add_comment(self, author, comment_text, visibility="public"):
        """Adds a comment to the ticket in JSON format."""
        if visibility == "internal" and author.role not in ["Controller", "SuperAdmin"]:
            raise ValidationError("Only Controllers and Admins can post internal comments.")

        new_comment = {
            "author_id": author.id,
            "author_name": author.name,
            "comment": comment_text,
            "visibility": visibility,
            "created_at": now().isoformat(),
        }

        self.comments.append(new_comment)
        self.save(update_fields=["comments"])

    def approve_ticket(self):
        """Approves a ticket and assigns it to the least busy controller based on category."""
        if self.status != "open":
            raise ValidationError("Only open tickets can be approved.")

        self.status = "in_progress"
        self.assign_controller()
        self.save(update_fields=["status", "assigned_controller"])

    def reject_ticket(self):
        """Rejects a ticket and marks it as closed."""
        if self.status == "closed":
            raise ValidationError("This ticket is already closed.")
        
        self.status = "closed"
        self.save(update_fields=["status"])

    def assign_controller(self):
        """Automatically assigns the least busy controller in the same category."""
        from users.models import CustomUser  # Import here to avoid circular imports

        available_controllers = (
            CustomUser.objects.filter(role="Controller", controller_type=self.category)
            .annotate(ticket_count=Count("assigned_tickets"))
            .order_by("ticket_count")
        )

        if available_controllers.exists():
            self.assigned_controller = available_controllers.first()
            print(f"✅ Ticket {self.ticket_id} assigned to {self.assigned_controller.name}")
