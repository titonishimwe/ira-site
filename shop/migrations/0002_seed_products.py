from django.db import migrations

CLOTHES = "S, M, L, XL"
SHOES = "38, 39, 40, 41, 42, 43, 44"

CATALOG = {
    "stationery": [
        ("School", [
            ("A4 Exercise Book, 96 pages", 1000, ""),
            ("School Backpack", 18000, ""),
            ("Geometry Set", 2500, ""),
            ("Ballpoint Pens, box of 50", 5000, ""),
            ("Colour Pencils, 24 pack", 3000, ""),
            ("Scientific Calculator", 12000, ""),
        ]),
        ("Office", [
            ("A4 Copy Paper, 500 sheets", 7500, ""),
            ("Ring Binder File", 2000, ""),
            ("Stapler with Staples", 3500, ""),
            ("Highlighters, set of 6", 2800, ""),
        ]),
        ("Printing", [
            ("Epson Ink Bottle, 70 ml", 9000, ""),
            ("Photo Paper A4, 20 sheets", 6000, ""),
        ]),
    ],
    "fashion": [
        ("Clothes", [
            ("Classic T-shirt", 8000, CLOTHES),
            ("Slim Fit Jeans", 25000, CLOTHES),
            ("Summer Dress", 22000, CLOTHES),
            ("Hoodie", 20000, CLOTHES),
            ("Formal Shirt", 15000, CLOTHES),
            ("Denim Jacket", 30000, CLOTHES),
        ]),
        ("Shoes", [
            ("Running Sneakers", 35000, SHOES),
            ("Leather Sandals", 18000, SHOES),
            ("Formal Leather Shoes", 40000, SHOES),
            ("Kids School Shoes", 14000, SHOES),
        ]),
    ],
}


def seed(apps, schema_editor):
    SiteSettings = apps.get_model("shop", "SiteSettings")
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")

    SiteSettings.objects.get_or_create(pk=1)
    for section, categories in CATALOG.items():
        for cat_order, (cat_name, products) in enumerate(categories):
            category, _ = Category.objects.get_or_create(
                section=section, name=cat_name, defaults={"sort_order": cat_order}
            )
            for order, (name, price, sizes) in enumerate(products):
                Product.objects.get_or_create(
                    category=category, name=name,
                    defaults={"price": price, "sizes": sizes, "sort_order": order},
                )


class Migration(migrations.Migration):
    dependencies = [("shop", "0001_initial")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
