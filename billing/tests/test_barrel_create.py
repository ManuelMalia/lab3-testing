from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel

User = get_user_model()

class BarrelCreateTests(APITestCase):
    def setUp(self):
        self.provider_a = Provider.objects.create(
            name="Provider A", address="Addr A", tax_id="TAX-A"
        )
        self.provider_b = Provider.objects.create(
            name="Provider B", address="Addr B", tax_id="TAX-B"
        )
        self.user_a = User.objects.create_user(
            username="user_a", password="pass1234", provider=self.provider_a
        )
        self.client.force_authenticate(user=self.user_a)

    def test_barrel_provider_is_taken_from_logged_in_user(self):
        payload = {
            "number": "B-001",
            "oil_type": "Olive",
            "liters": 100,
            "provider": self.provider_b.pk,
        }

        response = self.client.post(reverse("barrel-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        barrel = Barrel.objects.get(pk=response.data["id"])
        self.assertEqual(barrel.provider_id, self.provider_a.pk)
