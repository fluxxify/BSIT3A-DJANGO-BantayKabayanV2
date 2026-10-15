"""Declarative module registry for the Kabayani Track CRUD screens.

Each entry describes one monitoring/support module. The generic CRUD views in
``apps.ofw.crud`` use this metadata to build list pages, forms, and AJAX
endpoints so every module behaves consistently.
"""

from .models import (
    Concern,
    EmergencyHotline,
    FollowUp,
    OFW,
    Referral,
    StatusUpdate,
    SupportInfo,
    WelfareCheckIn,
)

MODULES = {
    'ofw': {
        'title': 'OFW Registry',
        'singular': 'OFW',
        'subtitle': 'Master list of monitored Overseas Filipino Workers',
        'icon': 'fas fa-passport',
        'model': OFW,
        'form_fields': [
            'full_name', 'sex', 'birth_date', 'contact_number', 'email',
            'home_address', 'passport_number', 'destination_country',
            'job_title', 'employer', 'agency', 'deployment_date',
            'contract_end_date', 'status', 'case_officer', 'notes',
        ],
        'auto_user_fields': [],
        'table_fields': [
            'full_name', 'destination_country', 'job_title', 'status', 'case_officer',
        ],
        'search_fields': [
            'full_name', 'passport_number', 'employer', 'agency',
            'destination_country', 'job_title',
        ],
    },
    'status': {
        'title': 'OFW Status Updates',
        'singular': 'Status Update',
        'subtitle': 'Reported changes to an OFW employment or personal status',
        'icon': 'fas fa-arrows-rotate',
        'model': StatusUpdate,
        'form_fields': ['ofw', 'status', 'report_date', 'remarks'],
        'auto_user_fields': ['reported_by'],
        'table_fields': ['ofw', 'status', 'report_date', 'reported_by'],
        'search_fields': ['ofw__full_name', 'status', 'remarks'],
    },
    'checkin': {
        'title': 'Welfare Check-ins',
        'singular': 'Welfare Check-in',
        'subtitle': 'Welfare monitoring and wellbeing assessments',
        'icon': 'fas fa-heart-pulse',
        'model': WelfareCheckIn,
        'form_fields': [
            'ofw', 'check_in_date', 'method', 'wellbeing',
            'follow_up_required', 'notes',
        ],
        'auto_user_fields': ['conducted_by'],
        'table_fields': ['ofw', 'check_in_date', 'method', 'wellbeing', 'follow_up_required'],
        'search_fields': ['ofw__full_name', 'wellbeing', 'method', 'notes'],
    },
    'concern': {
        'title': 'Reported Concerns',
        'singular': 'Concern',
        'subtitle': 'Cases, complaints, and issues reported for an OFW',
        'icon': 'fas fa-triangle-exclamation',
        'model': Concern,
        'form_fields': [
            'ofw', 'title', 'category', 'severity', 'status',
            'date_reported', 'description',
        ],
        'auto_user_fields': ['reported_by'],
        'table_fields': ['title', 'ofw', 'category', 'severity', 'status', 'date_reported'],
        'search_fields': ['title', 'ofw__full_name', 'category', 'description'],
    },
    'referral': {
        'title': 'Referrals',
        'singular': 'Referral',
        'subtitle': 'OFWs endorsed to service providers and partner agencies',
        'icon': 'fas fa-share-from-square',
        'model': Referral,
        'form_fields': [
            'ofw', 'concern', 'referred_to', 'status', 'date_referred',
            'reason', 'notes',
        ],
        'auto_user_fields': ['referred_by'],
        'table_fields': ['ofw', 'referred_to', 'concern', 'status', 'date_referred'],
        'search_fields': ['ofw__full_name', 'referred_to', 'reason'],
    },
    'followup': {
        'title': 'Follow-up Monitoring',
        'singular': 'Follow-up',
        'subtitle': 'Scheduled follow-ups for concerns and referrals',
        'icon': 'fas fa-list-check',
        'model': FollowUp,
        'form_fields': [
            'ofw', 'concern', 'referral', 'scheduled_date', 'status',
            'assigned_to', 'outcome',
        ],
        'auto_user_fields': [],
        'table_fields': ['ofw', 'scheduled_date', 'status', 'concern', 'assigned_to'],
        'search_fields': ['ofw__full_name', 'outcome', 'status'],
    },
    'support': {
        'title': 'Support Information',
        'singular': 'Support Info',
        'subtitle': 'Reference directory of support services and assistance',
        'icon': 'fas fa-circle-info',
        'model': SupportInfo,
        'form_fields': [
            'title', 'category', 'provider', 'contact', 'location',
            'website', 'description',
        ],
        'auto_user_fields': [],
        'table_fields': ['title', 'category', 'provider', 'contact', 'location'],
        'search_fields': ['title', 'provider', 'contact', 'description'],
    },
    'hotline': {
        'title': 'Emergency Hotlines',
        'singular': 'Emergency Hotline',
        'subtitle': 'Emergency and assistance contact numbers for OFWs',
        'icon': 'fas fa-phone-volume',
        'model': EmergencyHotline,
        'form_fields': [
            'name', 'category', 'organization', 'hotline_number',
            'alternate_number', 'coverage', 'available_hours', 'is_24_7',
            'email', 'website', 'address', 'notes',
        ],
        'auto_user_fields': [],
        'table_fields': ['name', 'category', 'hotline_number', 'coverage', 'is_24_7'],
        'search_fields': [
            'name', 'organization', 'hotline_number', 'coverage', 'category',
        ],
        'call_field': 'hotline_number',
    },
}

NAV_ORDER = ['ofw', 'checkin', 'concern', 'status', 'referral', 'followup', 'support', 'hotline']


def get_module(key):
    return MODULES.get(key)
