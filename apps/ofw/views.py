"""Dashboard views for Kabayani Track."""

import math

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .geo import city_for, coordinates_for, iso_for
from .models import (
    Concern,
    ConcernEscalation,
    EmergencyHotline,
    FollowUp,
    OFW,
    Referral,
    SupportInfo,
    WelfareCheckIn,
)
from .registry import MODULES

STATUS_COLORS = {
    OFW.Status.ACTIVE: '#2fb344',
    OFW.Status.ON_LEAVE: '#f59f00',
    OFW.Status.REPATRIATED: '#206bc4',
    OFW.Status.COMPLETED: '#0ca678',
    OFW.Status.DECEASED: '#d63939',
    OFW.Status.UNKNOWN: '#6c757d',
}


@login_required(login_url='login')
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('ofw:staff_dashboard')

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
        'hotlines': EmergencyHotline.objects.count(),
    }

    recent_concerns = Concern.objects.select_related('ofw')[:5]
    recent_checkins = WelfareCheckIn.objects.select_related('ofw')[:5]
    upcoming_followups = FollowUp.objects.select_related('ofw').filter(
        scheduled_date__gte=today,
        status=FollowUp.Status.SCHEDULED,
    )[:5]
    emergency_hotlines = EmergencyHotline.objects.all()[:6]

    escalations = ConcernEscalation.objects.select_related(
        'concern', 'concern__ofw', 'escalated_by'
    ).exclude(status=ConcernEscalation.Status.RESOLVED)

    return render(request, 'ofw/dashboard.html', {
        'stats': stats,
        'status_counts': status_counts,
        'recent_concerns': recent_concerns,
        'recent_checkins': recent_checkins,
        'upcoming_followups': upcoming_followups,
        'emergency_hotlines': emergency_hotlines,
        'escalations': escalations[:6],
        'escalation_count': escalations.count(),
        'nav_modules': [{'key': key, **MODULES[key]} for key in MODULES],
    })


@login_required(login_url='login')
def deployment_map(request):
    """World map marking where each monitored OFW is deployed."""

    markers = []
    status_counts = {}
    country_counts = {}
    unmapped = []
    seen = {}
    deployed_regions = set()

    for ofw in OFW.objects.select_related('case_officer'):
        coords = coordinates_for(ofw.destination_country)
        if not coords:
            unmapped.append(ofw.full_name)
            continue

        lat, lng = coords
        index = seen.get(ofw.destination_country, 0)
        seen[ofw.destination_country] = index + 1
        if index:
            angle = math.radians(index * 137.5)
            radius = 0.6 * math.sqrt(index)
            lat = lat + radius * math.sin(angle)
            lng = lng + radius * math.cos(angle)

        iso = iso_for(ofw.destination_country)
        if iso:
            deployed_regions.add(iso)

        markers.append({
            'id': ofw.pk,
            'name': ofw.full_name,
            'country': ofw.destination_country,
            'city': city_for(ofw.destination_country),
            'job_title': ofw.job_title or 'N/A',
            'employer': ofw.employer or 'N/A',
            'status': ofw.status or OFW.Status.UNKNOWN,
            'lat': round(lat, 5),
            'lng': round(lng, 5),
            'color': STATUS_COLORS.get(ofw.status, STATUS_COLORS[OFW.Status.UNKNOWN]),
            'label': city_for(ofw.destination_country) if index == 0 else '',
        })

        status_counts[ofw.status] = status_counts.get(ofw.status, 0) + 1
        country_counts[ofw.destination_country] = country_counts.get(ofw.destination_country, 0) + 1

    status_legend = [
        {'label': status, 'count': status_counts[status], 'color': STATUS_COLORS.get(status, STATUS_COLORS[OFW.Status.UNKNOWN])}
        for status in OFW.Status.values
        if status in status_counts
    ]
    country_legend = sorted(
        ({'label': country, 'count': count} for country, count in country_counts.items()),
        key=lambda row: (-row['count'], row['label']),
    )

    return render(request, 'ofw/map.html', {
        'markers': markers,
        'status_legend': status_legend,
        'country_legend': country_legend,
        'unmapped': unmapped,
        'total_ofw': OFW.objects.count(),
        'plotted': len(markers),
        'deployed_regions': sorted(deployed_regions),
    })


@login_required(login_url='login')
def staff_dashboard(request):
    """Staff workspace focused on OFW complaints and escalation to the admin.

    Staff see the complaints they can act on, can escalate any of them to the
    administrator, and can track whether the admin has acknowledged each
    escalation.
    """

    open_statuses = [Concern.Status.OPEN, Concern.Status.IN_PROGRESS]

    open_concerns = Concern.objects.select_related('ofw').filter(
        status__in=open_statuses
    ).order_by('-date_reported')[:10]

    escalations = ConcernEscalation.objects.select_related(
        'concern', 'concern__ofw', 'acknowledged_by'
    ).filter(escalated_by=request.user)

    stats = {
        'open_concerns': Concern.objects.filter(status__in=open_statuses).count(),
        'pending_escalations': escalations.filter(
            status=ConcernEscalation.Status.PENDING
        ).count(),
        'acknowledged': escalations.filter(
            status=ConcernEscalation.Status.ACKNOWLEDGED
        ).count(),
    }

    notified_concern_ids = set(escalations.values_list('concern_id', flat=True))

    return render(request, 'ofw/staff_dashboard.html', {
        'stats': stats,
        'open_concerns': open_concerns,
        'escalations': escalations[:10],
        'notified_concern_ids': notified_concern_ids,
    })


@login_required(login_url='login')
@require_POST
def escalate_concern(request, pk):
    """Escalate a concern to the administrator (staff -> admin link)."""

    concern = get_object_or_404(Concern, pk=pk)
    message = request.POST.get('message', '').strip()
    priority = request.POST.get('priority', ConcernEscalation.Priority.NORMAL)
    if priority not in ConcernEscalation.Priority.values:
        priority = ConcernEscalation.Priority.NORMAL

    ConcernEscalation.objects.create(
        concern=concern,
        message=message,
        priority=priority,
        escalated_by=request.user,
    )

    if concern.status == Concern.Status.OPEN:
        concern.status = Concern.Status.IN_PROGRESS
        concern.save(update_fields=['status', 'updated_at'])

    messages.success(
        request,
        f'Concern "{concern.title}" has been escalated to the administrator.',
    )
    return redirect('ofw:staff_dashboard')


@login_required(login_url='login')
@require_POST
def acknowledge_escalation(request, pk):
    """Administrator acknowledges an escalation and may send a response."""

    escalation = get_object_or_404(ConcernEscalation, pk=pk)
    escalation.status = ConcernEscalation.Status.ACKNOWLEDGED
    escalation.acknowledged_by = request.user
    escalation.acknowledged_at = timezone.now()
    response = request.POST.get('response', '').strip()
    if response:
        escalation.response = response
    escalation.save()

    messages.success(
        request,
        f'Escalation for "{escalation.concern.title}" acknowledged.',
    )
    return redirect(request.POST.get('next') or 'ofw:dashboard')
