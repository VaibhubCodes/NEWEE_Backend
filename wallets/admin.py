from django.contrib import admin
from .models import Wallet, Transaction, Referral, ReferralBonus, XamCoinConversion

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet_type', 'balance')
    search_fields = ('user__email', 'wallet_type')
    list_filter = ('wallet_type',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'wallet_user', 'transaction_type', 'amount', 'description', 'timestamp')
    search_fields = ('wallet__user__email', 'wallet__wallet_type', 'transaction_type', 'description')
    list_filter = ('transaction_type', 'wallet__wallet_type', 'timestamp')
    ordering = ('-timestamp',)

    @admin.display(description='User')
    def wallet_user(self, obj):
        return obj.wallet.user.email


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'created_at')
    search_fields = ('referrer__email', 'referred__email')
    list_filter = ('created_at',)


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ('referral_amount', 'referrer_amount')


@admin.register(XamCoinConversion)
class XamCoinConversionAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversion_rate', 'conversion_commission', 'is_active')
    list_editable = ('conversion_rate', 'conversion_commission', 'is_active')
    actions = ['make_active']

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            # Deactivate all other rules
            XamCoinConversion.objects.filter(is_active=True).update(is_active=False)
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark as Active")
    def make_active(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Only one rule can be active at a time.", level='error')
            return
        queryset.update(is_active=True)
        XamCoinConversion.objects.exclude(pk__in=queryset.values_list('id', flat=True)).update(is_active=False)
        self.message_user(request, "Selected rule is now active.", level='success')
