from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel, Invoice

User = get_user_model()

class BarrelDeleteTests(APITestCase):
    def setUp(self):
        self.provider = Provider.objects.create(
            name="Provider", address="Addr", tax_id="TAX-1"
        )
        self.admin = User.objects.create_superuser(username="admin", password="pass")
        self.client.force_authenticate(user=self.admin)

    def test_cannot_delete_billed_barrel(self):
        # Crear barril
        barrel = Barrel.objects.create(
            provider=self.provider, number="B-001", oil_type="Olive",
            liters=100, billed=False,
        )
        # Facturarlo
        invoice = Invoice.objects.create(
            provider=self.provider, invoice_no="INV-001", issued_on=date.today()
        )
        invoice.add_line_for_barrel(
            barrel=barrel,
            liters=100,
            unit_price_per_liter=Decimal("3.50"),
            description="Test",
        )

        # Intentar borrar el barril facturado
        url = reverse("barrel-detail", kwargs={"pk": barrel.pk})
        response = self.client.delete(url)

        # No debe permitirse — el barril sigue existiendo
        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Barrel.objects.filter(pk=barrel.pk).exists())
