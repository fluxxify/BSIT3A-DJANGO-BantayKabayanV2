"""Dashboard views for Kabayani Track."""

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from .models import Concern, FollowUp, OFW, Referral, SupportInfo, WelfareCheckIn
from .registry import MODULES


@login_required(login_url='login')
def dashboard(request):
    today = timezone.localdate()

    status_counts = (
        OFW.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    stats = {
        'ofw': OFW.objects.count(),
        'active': OFW.objects.filter(status=OFW.Status.ACTIVE).count(),
        'checkins': WelfareCheckIn.objects.count(),
        'open_concerns': Concern.objects.exclude(
            status__in=[Concern.Status.RESOLVED, Concern.Status.CLOSED]
        ).count(),
        'referrals': Referral.objects.filter(status=Referral.Status.PENDING).count(),
        'followups': FollowUp.objects.filter(
            status__in=[FollowUp.Status.SCHEDULED, FollowUp.Status.OVERDUE]
        ).count(),
        'support': SupportInfo.objects.count(),
    }

    recent_concerns = Concern.objects.select_related('ofw')[:5]
    recent_checkins = WelfareCheckIn.objects.select_related('ofw')[:5]
    upcoming_followups = FollowUp.objects.select_related('ofw').filter(
        scheduled_date__gte=today,
        status=FollowUp.Status.SCHEDULED,
    )[:5]

    return render(request, 'ofw/dashboard.html', {
        'stats': stats,
        'status_counts': status_counts,
        'recent_concerns': recent_concerns,
        'recent_checkins': recent_checkins,
        'upcoming_followups': upcoming_followups,
        'nav_modules': [{'key': key, **MODULES[key]} for key in MODULES],
    })
