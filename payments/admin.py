from django.contrib import admin
from .models import Payment, PayoutRequest

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'amount', 'status', 'created_at')
    search_fields = ('user__email', 'wallet__wallet_type', 'status')
    list_filter = ('status', 'wallet__wallet_type')


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet', 'amount', 'status', 'created_at')
    search_fields = ('user__email', 'wallet__wallet_type', 'status')
    list_filter = ('status',)
