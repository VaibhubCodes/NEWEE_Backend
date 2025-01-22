from django.urls import path
from .views import InitiatePaymentView,AddFundsView,VerifyPaymentView, ConfirmPaymentView,RejectPayoutView,PayoutListView, RequestPayoutView,WalletView,ApprovePayoutView

urlpatterns = [
    path('wallets/', WalletView.as_view(), name='wallets'),
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm_payment'),
    path("request-payout/", RequestPayoutView.as_view(), name="request_payout"),
    path("approve-payout/<int:payout_id>/", ApprovePayoutView.as_view(), name="approve_payout"),
    path("reject-payout/<int:payout_id>/", RejectPayoutView.as_view(), name="reject_payout"),
    path("payouts/", PayoutListView.as_view(), name="payout_list"), 
    path("add-funds/", AddFundsView.as_view(), name="add_funds"),
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify_payment"),
]
