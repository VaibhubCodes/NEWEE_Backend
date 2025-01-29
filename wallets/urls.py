from django.urls import path
from .views import (
    WalletView, CreditWalletView, DebitWalletView, TransactionHistoryView,
    ApplyReferralCodeView, XamCoinPurchaseView, XamCoinToMoneyConversionView, XamCoinConversionDetailsView, ReferralStatsView
)

urlpatterns = [
    path('wallets/', WalletView.as_view(), name='wallets'),
    path('wallets/credit/', CreditWalletView.as_view(), name='credit_wallet'),
    path('wallets/debit/', DebitWalletView.as_view(), name='debit_wallet'),
    path('wallets/transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('referral/apply/', ApplyReferralCodeView.as_view(), name='apply-referral'),
    path('xamcoins/purchase/', XamCoinPurchaseView.as_view(), name='xamcoins-purchase'),
    path('xamcoins/convert/', XamCoinToMoneyConversionView.as_view(), name='xamcoins-convert'),
    path('xamcoins/conversion-details/', XamCoinConversionDetailsView.as_view(), name='xamcoins-conversion-details'),
    path('referral/stats/', ReferralStatsView.as_view(), name='referral-stats'),
]
