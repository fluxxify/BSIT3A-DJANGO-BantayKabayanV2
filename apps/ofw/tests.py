from django.test import TestCase
from django.urls import reverse

from apps.ofw.models import Concern, OFW


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
