import json
import re

from django.test import Client, TestCase
from django.urls import reverse

from .models import OrderRequest, Product, SiteSettings


class PageTests(TestCase):
    def test_home(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Stationery &amp; Fashion")
        self.assertContains(response, 'data-whatsapp="250734244904"')

    def test_section_pages_list_seeded_products(self):
        response = self.client.get(reverse("stationery"))
        self.assertContains(response, "A4 Exercise Book, 96 pages")
        self.assertContains(response, "1,000 RWF")
        self.assertContains(response, 'data-filter="Printing"')
        self.assertNotContains(response, "size-select")

        response = self.client.get(reverse("fashion"))
        self.assertContains(response, "Running Sneakers")
        self.assertContains(response, "<option>44</option>")

    def test_hidden_products_are_not_shown(self):
        Product.objects.filter(name="Hoodie").update(is_active=False)
        self.assertNotContains(self.client.get(reverse("fashion")), "Hoodie")

    def test_settings_change_is_reflected(self):
        site = SiteSettings.load()
        site.whatsapp_number = "250788000000"
        site.save()
        self.assertContains(self.client.get(reverse("home")), 'data-whatsapp="250788000000"')

    def test_old_html_urls_redirect(self):
        self.assertRedirects(self.client.get("/fashion.html"), reverse("fashion"), status_code=301)


class ApiTests(TestCase):
    def post_order(self, payload):
        return self.client.post(reverse("api-order"), json.dumps(payload), content_type="application/json")

    def test_products_api_filters_by_section(self):
        data = self.client.get(reverse("api-products"), {"section": "fashion"}).json()
        self.assertEqual(len(data["products"]), 10)
        self.assertTrue(all(p["section"] == "fashion" for p in data["products"]))

    def test_order_is_recorded(self):
        jeans = Product.objects.get(name="Slim Fit Jeans")
        self.assertEqual(self.post_order({"product": jeans.pk, "size": "M"}).status_code, 201)
        order = OrderRequest.objects.get()
        self.assertEqual((order.product_name, order.size, order.price), ("Slim Fit Jeans", "M", 25000))

    def test_order_uses_csrf_token_from_page(self):
        client = Client(enforce_csrf_checks=True)
        html = client.get(reverse("fashion")).content.decode()
        token = re.search(r'data-csrf="([^"]+)"', html).group(1)
        body = json.dumps({"product": Product.objects.get(name="Hoodie").pk, "size": "L"})
        url = reverse("api-order")

        self.assertEqual(Client(enforce_csrf_checks=True).post(url, body, content_type="application/json").status_code, 403)
        self.assertEqual(client.post(url, body, content_type="application/json", HTTP_X_CSRFTOKEN=token).status_code, 201)

    def test_order_requires_valid_size(self):
        jeans = Product.objects.get(name="Slim Fit Jeans")
        self.assertEqual(self.post_order({"product": jeans.pk, "size": "XXXL"}).status_code, 400)
        self.assertEqual(self.post_order({"product": 999999}).status_code, 400)
        self.assertFalse(OrderRequest.objects.exists())
