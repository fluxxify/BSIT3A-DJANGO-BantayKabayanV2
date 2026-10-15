"""Kabayani Track domain models.

An OFW (Overseas Filipino Worker) Monitoring and Support Information System.
The app tracks OFW profiles together with their welfare check-ins, status
updates, reported concerns, support information, referrals, and follow-ups.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class OFW(models.Model):
    """Master record for an Overseas Filipino Worker being monitored."""

    class Sex(models.TextChoices):
        MALE = 'Male', 'Male'
        FEMALE = 'Female', 'Female'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        ON_LEAVE = 'On Leave', 'On Leave'
        REPATRIATED = 'Repatriated', 'Repatriated'
        COMPLETED = 'Completed', 'Completed'
        DECEASED = 'Deceased', 'Deceased'
        UNKNOWN = 'Unknown', 'Unknown'

    class DestinationCountry(models.TextChoices):
        SAUDI_ARABIA = 'Saudi Arabia', 'Saudi Arabia'
        UAE = 'UAE', 'United Arab Emirates (UAE)'
        QATAR = 'Qatar', 'Qatar'
        KUWAIT = 'Kuwait', 'Kuwait'
        BAHRAIN = 'Bahrain', 'Bahrain'
        OMAN = 'Oman', 'Oman'
        JORDAN = 'Jordan', 'Jordan'
        HONG_KONG = 'Hong Kong', 'Hong Kong'
        TAIWAN = 'Taiwan', 'Taiwan'
        SINGAPORE = 'Singapore', 'Singapore'
        MALAYSIA = 'Malaysia', 'Malaysia'
        JAPAN = 'Japan', 'Japan'
        SOUTH_KOREA = 'South Korea', 'South Korea'
        MACAU = 'Macau', 'Macau'
        ITALY = 'Italy', 'Italy'
        SPAIN = 'Spain', 'Spain'
        UK = 'United Kingdom', 'United Kingdom'
        GERMANY = 'Germany', 'Germany'
        CANADA = 'Canada', 'Canada'
        UNITED_STATES = 'United States', 'United States'
        OTHER = 'Other', 'Other'

    full_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10, choices=Sex.choices, default=Sex.MALE)
    birth_date = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    home_address = models.CharField(max_length=255, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)

    destination_country = models.CharField(
        max_length=100, choices=DestinationCountry.choices, default=DestinationCountry.OTHER
    )
    job_title = models.CharField(max_length=150, blank=True)
    employer = models.CharField(max_length=150, blank=True)
    agency = models.CharField(max_length=150, blank=True)

    deployment_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    case_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='ofw_cases',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblofw'
        ordering = ['full_name']
        verbose_name = 'OFW'
        verbose_name_plural = 'OFWs'

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )


class StatusUpdate(models.Model):
    """A reported change to an OFW's employment or personal status."""

    ofw = models.ForeignKey(OFW, related_name='status_updates', on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    report_date = models.DateField(default=timezone.localdate)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='status_updates',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_ofw_status_update'
        ordering = ['-report_date', '-id']
        verbose_name = 'OFW status update'
        verbose_name_plural = 'OFW status updates'

    def __str__(self):
        return f'{self.ofw.full_name} - {self.status}'


class WelfareCheckIn(models.Model):
    """A welfare check-in conducted for an OFW."""

    class Method(models.TextChoices):
        CALL = 'Call', 'Call'
        MESSAGE = 'Message', 'Message'
        HOME_VISIT = 'Home Visit', 'Home Visit'
        SOCIAL_MEDIA = 'Social Media', 'Social Media'
        OTHER = 'Other', 'Other'

    class Wellbeing(models.TextChoices):
        SAFE = 'Safe', 'Safe'
        NEEDS_ASSISTANCE = 'Needs Assistance', 'Needs Assistance'
        AT_RISK = 'At Risk', 'At Risk'
        UNREACHABLE = 'Unreachable', 'Unreachable'

    ofw = models.ForeignKey(OFW, related_name='check_ins', on_delete=models.CASCADE)
    check_in_date = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CALL)
    wellbeing = models.CharField(max_length=20, choices=Wellbeing.choices, default=Wellbeing.SAFE)
    notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='check_ins',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_ofw_check_in'
        ordering = ['-check_in_date', '-id']
        verbose_name = 'welfare check-in'
        verbose_name_plural = 'welfare check-ins'

    def __str__(self):
        return f'{self.ofw.full_name} - {self.wellbeing}'


class Concern(models.Model):
    """A concern reported about or by an OFW."""

    class Category(models.TextChoices):
        CONTRACT = 'Contract', 'Contract / Recruitment'
        ABUSE = 'Abuse', 'Abuse / Maltreatment'
        HEALTH = 'Health', 'Health'
        NON_PAYMENT = 'Non-payment', 'Non-payment of Salary'
        WORK_CONDITIONS = 'Working Conditions', 'Working Conditions'
        IMMIGRATION = 'Immigration', 'Immigration / Documentation'
        FINANCIAL = 'Financial', 'Financial Difficulty'
        OTHER = 'Other', 'Other'

    class Severity(models.TextChoices):
        LOW = 'Low', 'Low'
        MEDIUM = 'Medium', 'Medium'
        HIGH = 'High', 'High'
        CRITICAL = 'Critical', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'Open', 'Open'
        IN_PROGRESS = 'In Progress', 'In Progress'
        RESOLVED = 'Resolved', 'Resolved'
        CLOSED = 'Closed', 'Closed'

    ofw = models.ForeignKey(OFW, related_name='concerns', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.LOW)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    description = models.TextField(blank=True)
    date_reported = models.DateField(default=timezone.localdate)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='concerns',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_ofw_concern'
        ordering = ['-date_reported', '-id']
        verbose_name = 'reported concern'
        verbose_name_plural = 'reported concerns'

    def __str__(self):
        return self.title


class ConcernEscalation(models.Model):
    """An alert raised by staff to the administrator about an OFW concern.

    This is the link between the staff dashboard and the administrator: when
    staff escalates a complaint, an escalation record appears on the admin
    dashboard until it is acknowledged.
    """

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACKNOWLEDGED = 'Acknowledged', 'Acknowledged'
        RESOLVED = 'Resolved', 'Resolved'

    class Priority(models.TextChoices):
        NORMAL = 'Normal', 'Normal'
        URGENT = 'Urgent', 'Urgent'

    concern = models.ForeignKey(
        Concern,
        related_name='escalations',
        on_delete=models.CASCADE,
    )
    message = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='concern_escalations',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='acknowledged_escalations',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_ofw_concern_escalation'
        ordering = ['-created_at', '-id']
        verbose_name = 'concern escalation'
        verbose_name_plural = 'concern escalations'

    def __str__(self):
        return f'{self.concern.title} -> admin ({self.status})'


class SupportInfo(models.Model):
    """Reference information about available support services."""

    class Category(models.TextChoices):
        GOVERNMENT = 'Government Agency', 'Government Agency'
        EMBASSY = 'Embassy / Consulate', 'Embassy / Consulate'
        NGO = 'NGO', 'NGO'
        LEGAL = 'Legal Aid', 'Legal Aid'
        FINANCIAL = 'Financial Assistance', 'Financial Assistance'
        HEALTH = 'Health', 'Health'
        HOTLINE = 'Hotline', 'Hotline'
        OTHER = 'Other', 'Other'

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    provider = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_ofw_support_info'
        ordering = ['title']
        verbose_name = 'support information'
        verbose_name_plural = 'support information'

    def __str__(self):
        return self.title


class EmergencyHotline(models.Model):
    """An emergency contact number OFWs and families can reach for help."""

    class Category(models.TextChoices):
        EMERGENCY = 'Emergency', 'Emergency'
        POLICE = 'Police', 'Police'
        MEDICAL = 'Medical', 'Medical'
        FIRE = 'Fire', 'Fire'
        SEA_RESCUE = 'Sea Rescue', 'Sea Rescue'
        EMBASSY = 'Embassy / Consulate', 'Embassy / Consulate'
        POLO = 'Labor / POLO', 'Labor / POLO'
        GOVERNMENT = 'Government Agency', 'Government Agency'
        OTHER = 'Other', 'Other'

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.EMERGENCY)
    organization = models.CharField(max_length=255, blank=True)
    hotline_number = models.CharField(max_length=50)
    alternate_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    website = models.URLField(max_length=255, blank=True)
    coverage = models.CharField(max_length=150, blank=True, help_text='Country or area covered')
    available_hours = models.CharField(max_length=100, blank=True, help_text='e.g. 24/7 or 8am-5pm')
    is_24_7 = models.BooleanField(default=False, verbose_name='Available 24/7')
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tbl_ofw_emergency_hotline'
        ordering = ['-is_24_7', 'name']
        verbose_name = 'emergency hotline'
        verbose_name_plural = 'emergency hotlines'

    def __str__(self):
        return self.name


class Referral(models.Model):
    """A referral of an OFW (usually tied to a concern) to a service provider."""

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACCEPTED = 'Accepted', 'Accepted'
        COMPLETED = 'Completed', 'Completed'
        DECLINED = 'Declined', 'Declined'

    ofw = models.ForeignKey(OFW, related_name='referrals', on_delete=models.CASCADE)
    concern = models.ForeignKey(
        Concern,
        related_name='referrals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    referred_to = models.CharField(max_length=255)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    date_referred = models.DateField(default=timezone.localdate)
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referrals',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_ofw_referral'
        ordering = ['-date_referred', '-id']
        verbose_name = 'referral'
        verbose_name_plural = 'referrals'

    def __str__(self):
        return f'{self.ofw.full_name} -> {self.referred_to}'


class FollowUp(models.Model):
    """Follow-up monitoring task for a concern and/or referral."""

    class Status(models.TextChoices):
        SCHEDULED = 'Scheduled', 'Scheduled'
        COMPLETED = 'Completed', 'Completed'
        CANCELLED = 'Cancelled', 'Cancelled'
        OVERDUE = 'Overdue', 'Overdue'

    ofw = models.ForeignKey(OFW, related_name='follow_ups', on_delete=models.CASCADE)
    concern = models.ForeignKey(
        Concern,
        related_name='follow_ups',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    referral = models.ForeignKey(
        Referral,
        related_name='follow_ups',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    scheduled_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    outcome = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follow_ups',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tbl_ofw_follow_up'
        ordering = ['scheduled_date', '-id']
        verbose_name = 'follow-up'
        verbose_name_plural = 'follow-ups'

    def __str__(self):
        return f'{self.ofw.full_name} - {self.scheduled_date}'
