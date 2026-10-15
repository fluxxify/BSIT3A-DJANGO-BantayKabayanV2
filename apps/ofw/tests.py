from django.test import TestCase
from django.urls import reverse

from apps.ofw.models import Concern, ConcernEscalation, OFW


class OFWModelTests(TestCase):
    def test_age_calculation(self):
        from datetime import date

        ofw = OFW(full_name='Juan Dela Cruz', birth_date=date(1990, 1, 1))
        today = date.today()
        expected = today.year - 1990 - ((today.month, today.day) < (1, 1))
        self.assertEqual(ofw.age, expected)

    def test_str(self):
        ofw = OFW(full_name='Maria Santos')
        self.assertEqual(str(ofw), 'Maria Santos')


class ModuleViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_user(
            username='officer', password='secret1234'
        )
        self.client.force_login(self.user)

    def test_ofw_list_renders(self):
        OFW.objects.create(full_name='Juan Dela Cruz', destination_country='Qatar')
        response = self.client.get(reverse('ofw:module_list', args=['ofw']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan Dela Cruz')

    def test_create_ofw_via_ajax(self):
        response = self.client.post(reverse('ofw:module_save_ajax', args=['ofw']), {
            'full_name': 'Maria Santos',
            'sex': 'Female',
            'destination_country': 'Saudi Arabia',
            'status': 'Active',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OFW.objects.filter(full_name='Maria Santos').exists())

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('ofw:module_list', args=['ofw']))
        self.assertEqual(response.status_code, 302)

    def test_concern_auto_assigns_reporter(self):
        ofw = OFW.objects.create(full_name='Juan Dela Cruz', destination_country='Qatar')
        response = self.client.post(reverse('ofw:module_save_ajax', args=['concern']), {
            'ofw': ofw.pk,
            'title': 'Unpaid salary',
            'category': 'Non-payment',
            'severity': 'High',
            'status': 'Open',
        })
        self.assertEqual(response.status_code, 200)
        concern = Concern.objects.get(title='Unpaid salary')
        self.assertEqual(concern.reported_by, self.user)


class EscalationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.staff = User.objects.create_user(username='staff', password='secret1234')
        self.admin = User.objects.create_superuser(username='boss', password='secret1234')
        self.ofw = OFW.objects.create(full_name='Juan Dela Cruz', destination_country='Qatar')

    def _concern(self):
        return Concern.objects.create(
            ofw=self.ofw, title='Unpaid salary', reported_by=self.staff
        )

    def test_staff_dashboard_requires_login(self):
        response = self.client.get(reverse('ofw:staff_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_staff_dashboard_renders(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('ofw:staff_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_open_admin_dashboard(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('ofw:dashboard'))
        self.assertRedirects(response, reverse('ofw:staff_dashboard'))

    def test_admin_can_open_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('ofw:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_escalate_concern_to_admin(self):
        concern = self._concern()
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('ofw:escalate_concern', args=[concern.pk]),
            {'message': 'Needs admin attention', 'priority': 'Urgent'},
        )
        self.assertRedirects(response, reverse('ofw:staff_dashboard'))
        escalation = ConcernEscalation.objects.get(concern=concern)
        self.assertEqual(escalation.escalated_by, self.staff)
        self.assertEqual(escalation.status, ConcernEscalation.Status.PENDING)
        concern.refresh_from_db()
        self.assertEqual(concern.status, Concern.Status.IN_PROGRESS)

    def test_admin_sees_and_acknowledges_escalation(self):
        concern = self._concern()
        escalation = ConcernEscalation.objects.create(
            concern=concern, escalated_by=self.staff, priority='Urgent'
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse('ofw:dashboard'))
        self.assertContains(response, 'Staff Escalations')

        response = self.client.post(
            reverse('ofw:acknowledge_escalation', args=[escalation.pk]),
            {'response': 'On it.', 'next': reverse('ofw:dashboard')},
        )
        self.assertRedirects(response, reverse('ofw:dashboard'))
        escalation.refresh_from_db()
        self.assertEqual(escalation.status, ConcernEscalation.Status.ACKNOWLEDGED)
        self.assertEqual(escalation.acknowledged_by, self.admin)
