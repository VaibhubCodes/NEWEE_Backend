from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SupportTicket
from .serializers import SupportTicketSerializer, AddCommentSerializer
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models import Q

class CreateTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SupportTicketSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response({"message": "Ticket created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get('search', '')
        queryset = SupportTicket.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(ticket_id__icontains=search) |
                Q(student__name__icontains=search)
            )
        
        # Add other filters
        if category := request.query_params.get('category'):
            queryset = queryset.filter(category=category)
        
        if priority := request.query_params.get('priority'):
            queryset = queryset.filter(priority=priority)

        if status := request.query_params.get('status'):
            queryset = queryset.filter(status=status)
        # Similar for priority and status
        serializer = SupportTicketSerializer(queryset, many=True)
        return Response(serializer.data)
class RetrieveTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        serializer = SupportTicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

        if request.user.role not in ["SuperAdmin", "Controller"]:
            return Response({"error": "You do not have permission to update this ticket."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SupportTicketSerializer(ticket, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            if "priority" in request.data:
                ticket.due_date = now() + timedelta(hours=ticket.SLA_TIMEFRAMES.get(request.data["priority"], 48))
                ticket.save()
            return Response({"message": "Ticket updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveRejectTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_id, action):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

        if request.user.role not in ["SuperAdmin"]:
            return Response({"error": "Only SuperAdmins can approve or reject tickets."}, status=status.HTTP_403_FORBIDDEN)

        if action == "approve":
            try:
                ticket.approve_ticket()
                return Response({"message": f"Ticket {ticket.ticket_id} approved and assigned."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif action == "reject":
            try:
                ticket.reject_ticket()
                return Response({"message": "Ticket rejected successfully."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

class AddTicketCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        serializer = AddCommentSerializer(data=request.data)

        if serializer.is_valid():
            ticket.add_comment(author=request.user, comment_text=serializer.validated_data["comment"], visibility=serializer.validated_data["visibility"])
            return Response({"message": "Comment added successfully.", "comments": ticket.comments}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Ensure ListTicketCommentsView handles GET properly
class ListTicketCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        return Response({
            "ticket_id": str(ticket.ticket_id),
            "comments": ticket.comments
        }, status=status.HTTP_200_OK)
    
class AssignTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
        
        if request.user.role not in ["SuperAdmin", "Controller"]:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        try:
            ticket.assign_controller()
            ticket.status = "in_progress"
            ticket.save()
            return Response({
                "message": f"Ticket assigned to {ticket.assigned_controller.name}",
                "assigned_controller": {
                    "id": ticket.assigned_controller.id,
                    "name": ticket.assigned_controller.name
                }
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "No available controllers"}, status=status.HTTP_400_BAD_REQUEST)
        
