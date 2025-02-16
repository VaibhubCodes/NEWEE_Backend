from django.urls import path
from .views import (
    CreateTicketView, ListTicketsView, RetrieveTicketView, UpdateTicketView,
    ApproveRejectTicketView, AddTicketCommentView, ListTicketCommentsView,AssignTicketView
)

urlpatterns = [
    # 🎟 **Ticket Management**
    path("tickets/create/", CreateTicketView.as_view(), name="create-ticket"),
    path("tickets/", ListTicketsView.as_view(), name="list-tickets"),
    path("tickets/<uuid:ticket_id>/", RetrieveTicketView.as_view(), name="retrieve-ticket"),
    path("tickets/<uuid:ticket_id>/update/", UpdateTicketView.as_view(), name="update-ticket"),
    path("tickets/<uuid:ticket_id>/assign/", AssignTicketView.as_view(), name="assign-ticket"),
    
    # ✅ **Approve or Reject Tickets**
    path("tickets/<uuid:ticket_id>/<str:action>/", ApproveRejectTicketView.as_view(), name="approve-reject-ticket"),

    # ✅ **Add Comments to Ticket**
    path("tickets/<uuid:ticket_id>/comments/add/", AddTicketCommentView.as_view(), name="add-ticket-comment"),
    path("tickets/<uuid:ticket_id>/comments/", ListTicketCommentsView.as_view(), name="list-ticket-comments"),
]
