from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Invoice

User = get_user_model()

class InvoiceScopingTests(APITestCase):
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
        self.invoice_a = Invoice.objects.create(
            provider=self.provider_a, invoice_no="INV-A", issued_on=date.today()
        )
        self.invoice_b = Invoice.objects.create(
            provider=self.provider_b, invoice_no="INV-B", issued_on=date.today()
        )
        self.client.force_authenticate(user=self.user_a)

    def test_list_returns_only_own_provider_invoices(self):
        response = self.client.get(reverse("invoice-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [inv["id"] for inv in response.data]
        self.assertIn(self.invoice_a.pk, ids)
        self.assertNotIn(self.invoice_b.pk, ids)

    def test_detail_of_other_provider_invoice_returns_404(self):
        url = reverse("invoice-detail", kwargs={"pk": self.invoice_b.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
