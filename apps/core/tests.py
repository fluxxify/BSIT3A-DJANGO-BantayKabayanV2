from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_redirects_staff_to_staff_dashboard(self):
        user = get_user_model().objects.create_user(username='staff', password='secret1234')

        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('ofw:staff_dashboard'))

    def test_home_redirects_superuser_to_ofw_dashboard(self):
        user = get_user_model().objects.create_superuser(
            username='admin', password='secret1234'
        )

        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, reverse('ofw:dashboard'))

    def test_home_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
