from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel


User = get_user_model()


class ProviderEndpointTests(APITestCase):
    def test_provider_list_returns_name_and_tax_id(self):
        provider = Provider.objects.create(
            name="Acme Oils",
            address="Main St 1",
            tax_id="TAX-12345",
        )
        user = User.objects.create_user(
            username="provider_user",
            password="strongpass123",
            provider=provider,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("name", response.data[0])
        self.assertIn("tax_id", response.data[0])
        self.assertEqual(response.data[0]["name"], provider.name)
        self.assertEqual(response.data[0]["tax_id"], provider.tax_id)

    def test_superuser_sees_all_providers(self):
        Provider.objects.create(name="P1", address="A1", tax_id="T1")
        Provider.objects.create(name="P2", address="A2", tax_id="T2")
        admin = User.objects.create_superuser(username="admin", password="pass")
        self.client.force_authenticate(user=admin)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_regular_user_sees_only_own_provider(self):
        p1 = Provider.objects.create(name="P1", address="A1", tax_id="T1")
        Provider.objects.create(name="P2", address="A2", tax_id="T2")
        user = User.objects.create_user(username="u1", password="pass", provider=p1)
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], p1.pk)

    def test_regular_user_cannot_access_other_provider_detail(self):
        p1 = Provider.objects.create(name="P1", address="A1", tax_id="T1")
        p2 = Provider.objects.create(name="P2", address="A2", tax_id="T2")
        user = User.objects.create_user(username="u1", password="pass", provider=p1)
        self.client.force_authenticate(user=user)

        url = reverse("provider-detail", kwargs={"pk": p2.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_liters_billed_and_liters_to_bill(self):
        p = Provider.objects.create(name="P1", address="A1", tax_id="T1")
        Barrel.objects.create(provider=p, number="B1", oil_type="Olive", liters=100, billed=True)
        Barrel.objects.create(provider=p, number="B2", oil_type="Olive", liters=50, billed=False)
        admin = User.objects.create_superuser(username="admin", password="pass")
        self.client.force_authenticate(user=admin)

        url = reverse("provider-detail", kwargs={"pk": p.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["billed_liters"], 100)
        self.assertEqual(response.data["liters_to_bill"], 50)
