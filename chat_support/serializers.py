from rest_framework import serializers
from .models import SupportTicket

class SupportTicketSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    assigned_controller_name = serializers.CharField(source="assigned_controller.name", read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "ticket_id", "student", "student_name", "assigned_controller",
            "assigned_controller_name", "subject", "description", "category",
            "priority", "status", "created_at", "updated_at", "due_date", "comments"
        ]
        read_only_fields = ["ticket_id", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        """Ensures that ticket updates correctly."""
        if "comments" in validated_data:
            raise serializers.ValidationError({"error": "Comments should be updated via the dedicated add_comment function."})
        return super().update(instance, validated_data)

class AddCommentSerializer(serializers.Serializer):
    comment = serializers.CharField()
    visibility = serializers.ChoiceField(choices=["public", "internal"])

