from django.contrib import admin

from .models import (
    Concern,
    ConcernEscalation,
    FollowUp,
    OFW,
    Referral,
    StatusUpdate,
    SupportInfo,
    WelfareCheckIn,
)


@admin.register(OFW)
class OFWAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'destination_country', 'job_title', 'status', 'case_officer')
    list_filter = ('status', 'destination_country', 'sex')
    search_fields = ('full_name', 'passport_number', 'employer', 'agency', 'destination_country')


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('ofw', 'status', 'report_date', 'reported_by')
    list_filter = ('status',)
    search_fields = ('ofw__full_name', 'status')


@admin.register(WelfareCheckIn)
class WelfareCheckInAdmin(admin.ModelAdmin):
    list_display = ('ofw', 'check_in_date', 'method', 'wellbeing', 'follow_up_required')
    list_filter = ('wellbeing', 'method', 'follow_up_required')
    search_fields = ('ofw__full_name',)


@admin.register(Concern)
class ConcernAdmin(admin.ModelAdmin):
    list_display = ('title', 'ofw', 'category', 'severity', 'status', 'date_reported')
    list_filter = ('category', 'severity', 'status')
    search_fields = ('title', 'ofw__full_name')


@admin.register(SupportInfo)
class SupportInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'provider', 'contact')
    list_filter = ('category',)
    search_fields = ('title', 'provider', 'description')


@admin.register(ConcernEscalation)
class ConcernEscalationAdmin(admin.ModelAdmin):
    list_display = ('concern', 'priority', 'status', 'escalated_by', 'acknowledged_by', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('concern__title', 'concern__ofw__full_name', 'escalated_by__username')


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('ofw', 'referred_to', 'status', 'date_referred')
    list_filter = ('status',)
    search_fields = ('ofw__full_name', 'referred_to')


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('ofw', 'scheduled_date', 'status', 'assigned_to')
    list_filter = ('status',)
    search_fields = ('ofw__full_name',)
