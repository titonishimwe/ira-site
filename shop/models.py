from django.core.exceptions import ValidationError
from django.db import models


class SiteSettings(models.Model):
    store_name = models.CharField(max_length=60, default="Ira")
    whatsapp_number = models.CharField(
        max_length=20,
        default="250734244904",
        help_text="Country code + number, digits only (no '+' or spaces).",
    )
    phone_display = models.CharField(
        max_length=30, default="0734 244 904", help_text="Phone number as shown in the footer."
    )

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self):
        return "Site settings"

    def clean(self):
        if not self.whatsapp_number.isdigit():
            raise ValidationError({"whatsapp_number": "Use digits only, e.g. 250734244904."})

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Section(models.TextChoices):
    STATIONERY = "stationery", "Stationery"
    FASHION = "fashion", "Fashion"


class Category(models.Model):
    section = models.CharField(max_length=20, choices=Section.choices)
    name = models.CharField(max_length=60)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["section", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["section", "name"], name="unique_category_per_section"),
        ]

    def __str__(self):
        return f"{self.get_section_display()} / {self.name}"


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def in_section(self, section):
        return self.filter(category__section=section)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField(help_text="Price in RWF.")
    image = models.ImageField(upload_to="products/", blank=True)
    sizes = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated, e.g. 'S, M, L, XL' or '38, 39, 40'. Leave empty if no size is needed.",
    )
    is_active = models.BooleanField("visible on site", default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["category__sort_order", "sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def size_list(self):
        return [s.strip() for s in self.sizes.split(",") if s.strip()]


class OrderRequest(models.Model):
    """An order a customer started from the site; the conversation itself continues on WhatsApp."""

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="order_requests")
    product_name = models.CharField(max_length=120)
    price = models.PositiveIntegerField()
    size = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_name} ({self.created_at:%Y-%m-%d %H:%M})"
