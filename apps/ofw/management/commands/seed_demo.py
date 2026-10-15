"""Populate the database with example records for every Kabayani Track feature.

The command is safe to run multiple times: records are matched on a natural
key (for example the OFW full name or the concern title) and are only created
when missing. Use ``--reset`` to remove the example records first.

Usage::

    python manage.py seed_demo
    python manage.py seed_demo --reset
    python manage.py seed_demo --password demo12345

"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.ofw.models import (
    Concern,
    EmergencyHotline,
    FollowUp,
    OFW,
    Referral,
    StatusUpdate,
    SupportInfo,
    WelfareCheckIn,
)

User = get_user_model()

DEMO_OFFICERS = [
    {'username': 'maria.santos', 'first_name': 'Maria', 'last_name': 'Santos', 'email': 'maria.santos@dole.gov.ph'},
    {'username': 'jose.reyes', 'first_name': 'Jose', 'last_name': 'Reyes', 'email': 'jose.reyes@dole.gov.ph'},
    {'username': 'ana.delacruz', 'first_name': 'Ana', 'last_name': 'Dela Cruz', 'email': 'ana.delacruz@dole.gov.ph'},
]

DEMO_OFWS = [
    {
        'full_name': 'Juan Dela Cruz', 'sex': 'Male', 'birth_date': '1988-03-12',
        'contact_number': '+63 917 555 0101', 'email': 'juan.delacruz@example.com',
        'home_address': 'Cebu City, Cebu', 'passport_number': 'P1234567A',
        'destination_country': 'Saudi Arabia', 'job_title': 'Welder',
        'employer': 'Al Rajhi Construction', 'agency': 'Bright Future Manpower',
        'deployment_date': '2023-01-15', 'contract_end_date': '2025-01-14',
        'status': 'Active', 'officer': 'maria.santos',
        'notes': 'Regular contact every two weeks.',
    },
    {
        'full_name': 'Maria Clara Santos', 'sex': 'Female', 'birth_date': '1991-07-25',
        'contact_number': '+63 918 555 0102', 'email': 'maria.santos@example.com',
        'home_address': 'Quezon City, Metro Manila', 'passport_number': 'P2234567B',
        'destination_country': 'UAE', 'job_title': 'Registered Nurse',
        'employer': 'Al Noor Hospital', 'agency': 'Global Care Services',
        'deployment_date': '2022-05-10', 'contract_end_date': '2024-05-09',
        'status': 'Active', 'officer': 'jose.reyes',
        'notes': 'Requested contract renewal guidance.',
    },
    {
        'full_name': 'Pedro Penduko', 'sex': 'Male', 'birth_date': '1985-11-02',
        'contact_number': '+63 919 555 0103', 'email': 'pedro.penduko@example.com',
        'home_address': 'Davao City, Davao del Sur', 'passport_number': 'P3234567C',
        'destination_country': 'Qatar', 'job_title': 'Site Engineer',
        'employer': 'Doha Builders Inc.', 'agency': 'Prime Overseas',
        'deployment_date': '2021-09-01', 'contract_end_date': '2024-08-31',
        'status': 'On Leave', 'officer': 'ana.delacruz',
        'notes': 'On home leave until end of the month.',
    },
    {
        'full_name': 'Ana Liza Mercado', 'sex': 'Female', 'birth_date': '1993-02-18',
        'contact_number': '+63 920 555 0104', 'email': 'ana.mercado@example.com',
        'home_address': 'Iloilo City, Iloilo', 'passport_number': 'P4234567D',
        'destination_country': 'Hong Kong', 'job_title': 'Domestic Helper',
        'employer': 'Chan Family', 'agency': 'Sunrise Placement',
        'deployment_date': '2023-03-20', 'contract_end_date': '2025-03-19',
        'status': 'Active', 'officer': 'maria.santos',
        'notes': 'Reports weekly through messaging.',
    },
    {
        'full_name': 'Roberto Reyes', 'sex': 'Male', 'birth_date': '1982-06-30',
        'contact_number': '+63 921 555 0105', 'email': 'roberto.reyes@example.com',
        'home_address': 'Batangas City, Batangas', 'passport_number': 'P5234567E',
        'destination_country': 'Kuwait', 'job_title': 'Electrician',
        'employer': 'Gulf Electrical Works', 'agency': 'Star Manpower',
        'deployment_date': '2020-02-01', 'contract_end_date': '2024-01-31',
        'status': 'Active', 'officer': 'jose.reyes',
        'notes': 'Assisting with salary claim.',
    },
    {
        'full_name': 'Cristina Bautista', 'sex': 'Female', 'birth_date': '1990-09-14',
        'contact_number': '+63 922 555 0106', 'email': 'cristina.bautista@example.com',
        'home_address': 'Makati City, Metro Manila', 'passport_number': 'P6234567F',
        'destination_country': 'Singapore', 'job_title': 'IT Support Specialist',
        'employer': 'Lion City Tech', 'agency': 'Asia Talent Hub',
        'deployment_date': '2019-04-01', 'contract_end_date': '2022-03-31',
        'status': 'Completed', 'officer': 'ana.delacruz',
        'notes': 'Completed contract and returned home.',
    },
    {
        'full_name': 'Mark Anthony Villanueva', 'sex': 'Male', 'birth_date': '1994-12-05',
        'contact_number': '+63 923 555 0107', 'email': 'mark.villanueva@example.com',
        'home_address': 'Cagayan de Oro, Misamis Oriental', 'passport_number': 'P7234567G',
        'destination_country': 'Japan', 'job_title': 'Factory Worker',
        'employer': 'Hokkaido Manufacturing', 'agency': 'Nippon Placement',
        'deployment_date': '2023-06-15', 'contract_end_date': '2026-06-14',
        'status': 'Active', 'officer': 'maria.santos',
        'notes': 'Under technical intern program.',
    },
    {
        'full_name': 'Grace Ann Torres', 'sex': 'Female', 'birth_date': '1987-08-21',
        'contact_number': '+63 924 555 0108', 'email': 'grace.torres@example.com',
        'home_address': 'Bacolod City, Negros Occidental', 'passport_number': 'P8234567H',
        'destination_country': 'Italy', 'job_title': 'Caregiver',
        'employer': 'Famiglia Rossi', 'agency': 'Euro Care Link',
        'deployment_date': '2018-10-01', 'contract_end_date': '2023-09-30',
        'status': 'Repatriated', 'officer': 'jose.reyes',
        'notes': 'Repatriated after health concerns; now under reintegration.',
    },
    {
        'full_name': 'Ramon Alcantara', 'sex': 'Male', 'birth_date': '1979-01-09',
        'contact_number': '+63 925 555 0109', 'email': 'ramon.alcantara@example.com',
        'home_address': 'Tarlac City, Tarlac', 'passport_number': 'P9234567I',
        'destination_country': 'Saudi Arabia', 'job_title': 'Heavy Equipment Operator',
        'employer': 'Desert Star Contracting', 'agency': 'Prime Overseas',
        'deployment_date': '2017-05-01', 'contract_end_date': '2022-04-30',
        'status': 'Deceased', 'officer': 'ana.delacruz',
        'notes': 'Case closed; family assisted with benefits claim.',
    },
    {
        'full_name': 'Liezl Domingo', 'sex': 'Female', 'birth_date': '1995-04-27',
        'contact_number': '+63 926 555 0110', 'email': 'liezl.domingo@example.com',
        'home_address': 'Baguio City, Benguet', 'passport_number': 'P0234567J',
        'destination_country': 'Canada', 'job_title': 'Hotel Staff',
        'employer': 'Maple Leaf Resorts', 'agency': 'North Star Agency',
        'deployment_date': '2023-02-01', 'contract_end_date': '2025-01-31',
        'status': 'Active', 'officer': 'maria.santos',
        'notes': 'Adjusting well to winter schedule.',
    },
    {
        'full_name': 'Kevin Ramirez', 'sex': 'Male', 'birth_date': '1992-10-16',
        'contact_number': '+63 927 555 0111', 'email': 'kevin.ramirez@example.com',
        'home_address': 'Subic, Zambales', 'passport_number': 'P1334567K',
        'destination_country': 'South Korea', 'job_title': 'Shipyard Worker',
        'employer': 'Busan Marine Industries', 'agency': 'Pacific Workforce',
        'deployment_date': '2022-08-01', 'contract_end_date': '2025-07-31',
        'status': 'On Leave', 'officer': 'jose.reyes',
        'notes': 'Taking approved vacation leave.',
    },
    {
        'full_name': 'Divina Aquino', 'sex': 'Female', 'birth_date': '1989-05-30',
        'contact_number': '+63 928 555 0112', 'email': 'divina.aquino@example.com',
        'home_address': 'San Fernando, Pampanga', 'passport_number': 'P2334567L',
        'destination_country': 'Taiwan', 'job_title': 'Electronics Assembler',
        'employer': 'Taipei Electronics Co.', 'agency': 'Asia Talent Hub',
        'deployment_date': '2023-09-01', 'contract_end_date': '2026-08-31',
        'status': 'Active', 'officer': 'ana.delacruz',
        'notes': 'First-time OFW; regular check-ins scheduled.',
    },
]

DEMO_STATUS_UPDATES = [
    {'ofw': 'Pedro Penduko', 'status': 'On Leave', 'days': 5, 'remarks': 'Started approved home leave.'},
    {'ofw': 'Grace Ann Torres', 'status': 'Repatriated', 'days': 20, 'remarks': 'Returned to the Philippines; reintegration interview done.'},
    {'ofw': 'Cristina Bautista', 'status': 'Completed', 'days': 40, 'remarks': 'Contract completed, final settlement received.'},
    {'ofw': 'Roberto Reyes', 'status': 'Active', 'days': 3, 'remarks': 'Still employed; salary issue unresolved.'},
]

DEMO_CHECKINS = [
    {'ofw': 'Juan Dela Cruz', 'days': 2, 'method': 'Call', 'wellbeing': 'Safe', 'follow_up': False, 'notes': 'In good spirits.'},
    {'ofw': 'Ana Liza Mercado', 'days': 1, 'method': 'Message', 'wellbeing': 'Safe', 'follow_up': False, 'notes': 'Confirmed weekly update.'},
    {'ofw': 'Roberto Reyes', 'days': 4, 'method': 'Social Media', 'wellbeing': 'Needs Assistance', 'follow_up': True, 'notes': 'Repeated salary delays reported.'},
    {'ofw': 'Grace Ann Torres', 'days': 7, 'method': 'Home Visit', 'wellbeing': 'Needs Assistance', 'follow_up': True, 'notes': 'Needs medical follow-up at home.'},
    {'ofw': 'Divina Aquino', 'days': 6, 'method': 'Call', 'wellbeing': 'At Risk', 'follow_up': True, 'notes': 'Reports excessive working hours.'},
    {'ofw': 'Mark Anthony Villanueva', 'days': 3, 'method': 'Message', 'wellbeing': 'Safe', 'follow_up': False, 'notes': 'Settling in well.'},
    {'ofw': 'Ramon Alcantara', 'days': 30, 'method': 'Other', 'wellbeing': 'Unreachable', 'follow_up': False, 'notes': 'Recorded prior to case closure.'},
]

DEMO_CONCERNS = [
    {
        'ofw': 'Roberto Reyes', 'title': 'Unpaid salaries for two months',
        'category': 'Non-payment', 'severity': 'High', 'status': 'In Progress', 'days': 10,
        'description': 'Employer has delayed salary payments for two months despite follow-ups.',
    },
    {
        'ofw': 'Divina Aquino', 'title': 'Excessive working hours',
        'category': 'Working Conditions', 'severity': 'Medium', 'status': 'Open', 'days': 4,
        'description': 'Working over 12 hours a day with no overtime pay.',
    },
    {
        'ofw': 'Roberto Reyes', 'title': 'Passport held by employer',
        'category': 'Immigration', 'severity': 'Critical', 'status': 'Open', 'days': 2,
        'description': 'Passport was confiscated by the employer upon arrival.',
    },
    {
        'ofw': 'Grace Ann Torres', 'title': 'Medical assistance needed after repatriation',
        'category': 'Health', 'severity': 'High', 'status': 'Resolved', 'days': 15,
        'description': 'Referred to OWWA for medical assistance; approved.',
    },
    {
        'ofw': 'Juan Dela Cruz', 'title': 'Contract terms not followed',
        'category': 'Contract', 'severity': 'Low', 'status': 'Closed', 'days': 45,
        'description': 'Job description differed slightly from the signed contract; resolved.',
    },
]

DEMO_REFERRALS = [
    {
        'ofw': 'Roberto Reyes', 'concern': 'Unpaid salaries for two months',
        'referred_to': 'OWWA Welfare Assistance', 'status': 'Accepted', 'days': 8,
        'reason': 'Request for legal and financial assistance on unpaid wages.',
        'notes': 'Case officer assigned by OWWA.',
    },
    {
        'ofw': 'Divina Aquino', 'concern': 'Excessive working hours',
        'referred_to': 'POLO Taipei', 'status': 'Pending', 'days': 3,
        'reason': 'Request for workplace inspection and intervention.',
        'notes': 'Awaiting acknowledgement from POLO.',
    },
    {
        'ofw': 'Grace Ann Torres', 'concern': 'Medical assistance needed after repatriation',
        'referred_to': 'Department of Health - Regional Office', 'status': 'Completed', 'days': 12,
        'reason': 'Referral for free medical check-up package.',
        'notes': 'Patient completed consultation.',
    },
]

DEMO_FOLLOWUPS = [
    {
        'ofw': 'Roberto Reyes', 'concern': 'Unpaid salaries for two months',
        'referral': 'OWWA Welfare Assistance', 'status': 'Scheduled', 'days': 3,
        'officer': 'jose.reyes', 'outcome': '',
    },
    {
        'ofw': 'Divina Aquino', 'concern': 'Excessive working hours',
        'referral': 'POLO Taipei', 'status': 'Overdue', 'days': -2,
        'officer': 'ana.delacruz', 'outcome': '',
    },
    {
        'ofw': 'Grace Ann Torres', 'concern': 'Medical assistance needed after repatriation',
        'referral': 'Department of Health - Regional Office', 'status': 'Completed', 'days': -5,
        'officer': 'jose.reyes', 'outcome': 'Medical assistance provided; OFW recovered.',
    },
    {
        'ofw': 'Roberto Reyes', 'concern': 'Passport held by employer',
        'referral': None, 'status': 'Scheduled', 'days': 1,
        'officer': 'maria.santos', 'outcome': '',
    },
]

DEMO_SUPPORT_INFO = [
    {
        'title': 'OWWA Welfare Assistance Program', 'category': 'Government Agency',
        'provider': 'Overseas Workers Welfare Administration', 'contact': '(02) 8911-7311',
        'location': '7th St., Pasay City, Metro Manila', 'website': 'https://www.owwa.gov.ph',
        'description': 'Welfare, repatriation, and livelihood assistance for OFWs and their families.',
    },
    {
        'title': 'POLO Hotline - Saudi Arabia', 'category': 'Hotline',
        'provider': 'Philippine Overseas Labor Office', 'contact': '+966 11 000 0000',
        'location': 'Riyadh, Saudi Arabia', 'website': 'https://www.dmw.gov.ph',
        'description': '24/7 hotline for labor disputes and emergency assistance.',
    },
    {
        'title': 'Philippine Embassy in UAE', 'category': 'Embassy / Consulate',
        'provider': 'Department of Foreign Affairs', 'contact': '+971 2 222 0000',
        'location': 'Abu Dhabi, UAE', 'website': 'https://www.dfa.gov.ph',
        'description': 'Consular and assistance-to-nationals services.',
    },
    {
        'title': 'Legal Aid for Migrant Workers', 'category': 'Legal Aid',
        'provider': 'Migrante Legal Services', 'contact': '(02) 8123-4567',
        'location': 'Quezon City, Metro Manila', 'website': '',
        'description': 'Free legal advice and representation for labor cases abroad.',
    },
    {
        'title': 'Balik Pinay, Balik Hanapbuhay', 'category': 'Financial Assistance',
        'provider': 'DOLE / OWWA', 'contact': '(02) 8527-3000',
        'location': 'Intramuros, Manila', 'website': 'https://www.dole.gov.ph',
        'description': 'Livelihood starter kits and training for repatriated OFWs.',
    },
    {
        'title': 'OFW Health Support Network', 'category': 'Health',
        'provider': 'Department of Health', 'contact': '(02) 8651-7800',
        'location': 'San Lazaro, Manila', 'website': 'https://www.doh.gov.ph',
        'description': 'Medical referrals and psychosocial support for distressed OFWs.',
    },
]

DEMO_HOTLINES = [
    {
        'name': 'National Emergency Hotline', 'category': 'Emergency',
        'organization': 'Department of the Interior and Local Government',
        'hotline_number': '911', 'alternate_number': '', 'coverage': 'Philippines',
        'available_hours': '24/7', 'is_24_7': True, 'email': '', 'website': '',
        'address': '', 'notes': 'Unified national emergency hotline for police, fire, and medical response.',
    },
    {
        'name': 'PNP Emergency Hotline', 'category': 'Police',
        'organization': 'Philippine National Police', 'hotline_number': '117',
        'alternate_number': '(02) 8722-0650', 'coverage': 'Philippines',
        'available_hours': '24/7', 'is_24_7': True, 'email': '', 'website': 'https://www.pnp.gov.ph',
        'address': 'Camp Crame, Quezon City', 'notes': 'Report crimes and emergencies.',
    },
    {
        'name': 'Bureau of Fire Protection', 'category': 'Fire',
        'organization': 'Bureau of Fire Protection', 'hotline_number': '(02) 8426-0219',
        'alternate_number': '911', 'coverage': 'Philippines', 'available_hours': '24/7',
        'is_24_7': True, 'email': '', 'website': 'https://bfp.gov.ph', 'address': '',
        'notes': 'Fire and rescue response.',
    },
    {
        'name': 'Philippine Red Cross', 'category': 'Medical',
        'organization': 'Philippine Red Cross', 'hotline_number': '143',
        'alternate_number': '(02) 8790-2300', 'coverage': 'Philippines',
        'available_hours': '24/7', 'is_24_7': True, 'email': '', 'website': 'https://redcross.org.ph',
        'address': 'Port Area, Manila', 'notes': 'Ambulance and emergency medical services.',
    },
    {
        'name': 'Philippine Coast Guard', 'category': 'Sea Rescue',
        'organization': 'Philippine Coast Guard', 'hotline_number': '(02) 8527-8481',
        'alternate_number': '', 'coverage': 'Philippine waters', 'available_hours': '24/7',
        'is_24_7': True, 'email': '', 'website': 'https://coastguard.gov.ph', 'address': '',
        'notes': 'Maritime search and rescue.',
    },
    {
        'name': 'DOLE Hotline', 'category': 'Government Agency',
        'organization': 'Department of Labor and Employment', 'hotline_number': '1349',
        'alternate_number': '', 'coverage': 'Philippines / OFWs', 'available_hours': '24/7',
        'is_24_7': True, 'email': '', 'website': 'https://www.dole.gov.ph',
        'address': 'Intramuros, Manila', 'notes': 'Labor and employment concerns, including OFW cases.',
    },
    {
        'name': 'OWWA Assistance Hotline', 'category': 'Government Agency',
        'organization': 'Overseas Workers Welfare Administration', 'hotline_number': '8888',
        'alternate_number': '(02) 8911-7311', 'coverage': 'Philippines / OFWs',
        'available_hours': '24/7', 'is_24_7': True, 'email': '', 'website': 'https://www.owwa.gov.ph',
        'address': 'Pasay City, Metro Manila', 'notes': 'Welfare, repatriation, and livelihood assistance for OFWs.',
    },
    {
        'name': 'DFA Migrant Workers Affairs', 'category': 'Government Agency',
        'organization': 'Department of Foreign Affairs', 'hotline_number': '(02) 8834-4999',
        'alternate_number': '', 'coverage': 'Worldwide', 'available_hours': '24/7', 'is_24_7': True,
        'email': '', 'website': 'https://www.dfa.gov.ph', 'address': 'Roxas Blvd., Pasay City',
        'notes': 'Assistance-to-nationals for distressed OFWs.',
    },
    {
        'name': 'Philippine Embassy in Saudi Arabia', 'category': 'Embassy / Consulate',
        'organization': 'Department of Foreign Affairs', 'hotline_number': '+966 11 482 3555',
        'alternate_number': '', 'coverage': 'Saudi Arabia', 'available_hours': '24/7', 'is_24_7': True,
        'email': '', 'website': '', 'address': 'Riyadh, Saudi Arabia',
        'notes': 'Consular and assistance-to-nationals services.',
    },
    {
        'name': 'POLO Dubai', 'category': 'Labor / POLO',
        'organization': 'Philippine Overseas Labor Office', 'hotline_number': '+971 4 220 7100',
        'alternate_number': '', 'coverage': 'United Arab Emirates', 'available_hours': '8:00am - 5:00pm',
        'is_24_7': False, 'email': '', 'website': '', 'address': 'Dubai, UAE',
        'notes': 'Labor disputes and OFW assistance.',
    },
    {
        'name': 'OFW Help Hotline', 'category': 'Other',
        'organization': 'DFA - Office of the Undersecretary for Migrant Workers Affairs',
        'hotline_number': '(02) 8834-4999', 'alternate_number': '', 'coverage': 'Worldwide',
        'available_hours': '24/7', 'is_24_7': True, 'email': 'ofwhelp@dfa.gov.ph', 'website': '',
        'address': '', 'notes': 'Emergency assistance line for OFWs abroad.',
    },
]

DEMO_USERNAMES = [officer['username'] for officer in DEMO_OFFICERS]
DEMO_OFW_NAMES = [row['full_name'] for row in DEMO_OFWS]
DEMO_SUPPORT_TITLES = [row['title'] for row in DEMO_SUPPORT_INFO]
DEMO_HOTLINE_NAMES = [row['name'] for row in DEMO_HOTLINES]


class Command(BaseCommand):
    help = 'Create example records for every module (OFW, check-ins, concerns, status, referrals, follow-ups, support info).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete the example records before seeding.')
        parser.add_argument('--password', default=None, help='Password to assign to created demo users.')

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        if options['reset']:
            self._reset()

        officers = self._seed_officers(options['password'])
        ofws = self._seed_ofws(officers, today)
        status_count = self._seed_status_updates(officers, today)
        checkin_count = self._seed_checkins(officers, today)
        concern_count = self._seed_concerns(officers, today)
        referral_count = self._seed_referrals(officers, today)
        followup_count = self._seed_followups(officers, today)
        support_count = self._seed_support_info()
        hotline_count = self._seed_hotlines()

        self.stdout.write(self.style.SUCCESS(
            'Demo data ready: '
            f'{len(ofws)} OFWs, {status_count} status updates, {checkin_count} check-ins, '
            f'{concern_count} concerns, {referral_count} referrals, {followup_count} follow-ups, '
            f'{support_count} support entries, {hotline_count} hotlines, {len(officers)} officers.'
        ))

    def _reset(self):
        Referral.objects.filter(ofw__full_name__in=DEMO_OFW_NAMES).delete()
        FollowUp.objects.filter(ofw__full_name__in=DEMO_OFW_NAMES).delete()
        Concern.objects.filter(ofw__full_name__in=DEMO_OFW_NAMES).delete()
        WelfareCheckIn.objects.filter(ofw__full_name__in=DEMO_OFW_NAMES).delete()
        StatusUpdate.objects.filter(ofw__full_name__in=DEMO_OFW_NAMES).delete()
        OFW.objects.filter(full_name__in=DEMO_OFW_NAMES).delete()
        SupportInfo.objects.filter(title__in=DEMO_SUPPORT_TITLES).delete()
        EmergencyHotline.objects.filter(name__in=DEMO_HOTLINE_NAMES).delete()
        User.objects.filter(username__in=DEMO_USERNAMES).delete()
        self.stdout.write(self.style.WARNING('Removed existing example records.'))

    def _seed_officers(self, password):
        officers = {}
        for row in DEMO_OFFICERS:
            user, created = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'is_staff': True,
                },
            )
            if created:
                if password:
                    user.set_password(password)
                else:
                    user.set_unusable_password()
                user.save()
            officers[row['username']] = user
        return officers

    def _seed_ofws(self, officers, today):
        ofws = {}
        for row in DEMO_OFWS:
            data = dict(row)
            officer = officers.get(data.pop('officer'))
            full_name = data.pop('full_name')
            ofw, _ = OFW.objects.get_or_create(
                full_name=full_name,
                defaults={**data, 'case_officer': officer},
            )
            ofws[ofw.full_name] = ofw
        return ofws

    def _seed_status_updates(self, officers, today):
        count = 0
        for row in DEMO_STATUS_UPDATES:
            ofw = OFW.objects.filter(full_name=row['ofw']).first()
            if not ofw:
                continue
            report_date = today - timedelta(days=row['days'])
            _, created = StatusUpdate.objects.get_or_create(
                ofw=ofw,
                status=row['status'],
                report_date=report_date,
                defaults={
                    'remarks': row['remarks'],
                    'reported_by': officers.get('maria.santos'),
                },
            )
            count += created
        return count

    def _seed_checkins(self, officers, today):
        count = 0
        for row in DEMO_CHECKINS:
            ofw = OFW.objects.filter(full_name=row['ofw']).first()
            if not ofw:
                continue
            check_in_date = today - timedelta(days=row['days'])
            _, created = WelfareCheckIn.objects.get_or_create(
                ofw=ofw,
                check_in_date=check_in_date,
                method=row['method'],
                defaults={
                    'wellbeing': row['wellbeing'],
                    'notes': row['notes'],
                    'follow_up_required': row['follow_up'],
                    'conducted_by': officers.get('jose.reyes'),
                },
            )
            count += created
        return count

    def _seed_concerns(self, officers, today):
        count = 0
        for row in DEMO_CONCERNS:
            ofw = OFW.objects.filter(full_name=row['ofw']).first()
            if not ofw:
                continue
            date_reported = today - timedelta(days=row['days'])
            _, created = Concern.objects.get_or_create(
                ofw=ofw,
                title=row['title'],
                defaults={
                    'category': row['category'],
                    'severity': row['severity'],
                    'status': row['status'],
                    'description': row['description'],
                    'date_reported': date_reported,
                    'reported_by': officers.get('maria.santos'),
                },
            )
            count += created
        return count

    def _seed_referrals(self, officers, today):
        count = 0
        for row in DEMO_REFERRALS:
            ofw = OFW.objects.filter(full_name=row['ofw']).first()
            if not ofw:
                continue
            concern = Concern.objects.filter(ofw=ofw, title=row['concern']).first()
            date_referred = today - timedelta(days=row['days'])
            _, created = Referral.objects.get_or_create(
                ofw=ofw,
                referred_to=row['referred_to'],
                defaults={
                    'concern': concern,
                    'status': row['status'],
                    'date_referred': date_referred,
                    'reason': row['reason'],
                    'notes': row['notes'],
                    'referred_by': officers.get('ana.delacruz'),
                },
            )
            count += created
        return count

    def _seed_followups(self, officers, today):
        count = 0
        for row in DEMO_FOLLOWUPS:
            ofw = OFW.objects.filter(full_name=row['ofw']).first()
            if not ofw:
                continue
            concern = Concern.objects.filter(ofw=ofw, title=row['concern']).first() if row['concern'] else None
            referral = Referral.objects.filter(ofw=ofw, referred_to=row['referral']).first() if row['referral'] else None
            scheduled_date = today + timedelta(days=row['days'])
            _, created = FollowUp.objects.get_or_create(
                ofw=ofw,
                scheduled_date=scheduled_date,
                defaults={
                    'concern': concern,
                    'referral': referral,
                    'status': row['status'],
                    'outcome': row['outcome'],
                    'assigned_to': officers.get(row['officer']),
                },
            )
            count += created
        return count

    def _seed_support_info(self):
        count = 0
        for row in DEMO_SUPPORT_INFO:
            defaults = {k: v for k, v in row.items() if k != 'title'}
            _, created = SupportInfo.objects.get_or_create(title=row['title'], defaults=defaults)
            count += created
        return count

    def _seed_hotlines(self):
        count = 0
        for row in DEMO_HOTLINES:
            defaults = {k: v for k, v in row.items() if k != 'name'}
            _, created = EmergencyHotline.objects.get_or_create(name=row['name'], defaults=defaults)
            count += created
        return count
