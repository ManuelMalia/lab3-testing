from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel, Invoice, InvoiceLine

User = get_user_model()

class AddLineProviderMismatchTests(APITestCase):
    def setUp(self):
        
        self.provider_a = Provider.objects.create(
            name="Provider A", address="Addr A", tax_id="TAX-A"
        )
        self.provider_b = Provider.objects.create(
            name="Provider B", address="Addr B", tax_id="TAX-B"
        )
        self.user = User.objects.create_superuser(
            username="admin", password="adminpass"
        )
        self.client.force_authenticate(user=self.user)

        self.invoice_a = Invoice.objects.create(
            provider=self.provider_a,
            invoice_no="INV-001",
            issued_on=date.today(),
        )
        self.barrel_b = Barrel.objects.create(
            provider=self.provider_b,
            number="B-001",
            oil_type="Olive",
            liters=100,
            billed=False,
        )

    def test_cannot_add_barrel_from_different_provider(self):
        url = reverse("invoice-add-line", kwargs={"pk": self.invoice_a.pk})
        payload = {
            "barrel": self.barrel_b.pk,
            "liters": 100,
            "unit_price": "3.50",
            "description": "Test",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(InvoiceLine.objects.count(), 0)
        self.barrel_b.refresh_from_db()
        self.assertFalse(self.barrel_b.billed)
