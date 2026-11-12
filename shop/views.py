import json

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.http import require_GET, require_POST

from .models import Category, OrderRequest, Product, Section


def home(request):
    return render(request, "shop/home.html", {"nav": "home"})


def section_page(request, section):
    if section not in Section.values:
        raise Http404
    products = Product.objects.active().in_section(section).select_related("category")
    categories = Category.objects.filter(section=section, products__is_active=True).distinct()
    return render(
        request,
        "shop/section.html",
        {
            "nav": section,
            "section": section,
            "section_label": Section(section).label,
            "categories": categories,
            "products": products,
        },
    )


def _product_json(request, product):
    image = product.image.url if product.image else static("images/placeholder.svg")
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "section": product.category.section,
        "category": product.category.name,
        "sizes": product.size_list,
        "image": request.build_absolute_uri(image),
    }


@require_GET
def api_products(request):
    products = Product.objects.active().select_related("category")
    section = request.GET.get("section")
    if section:
        products = products.in_section(section)
    return JsonResponse({"products": [_product_json(request, p) for p in products]})


@require_POST
def api_order(request):
    try:
        data = json.loads(request.body)
        product = Product.objects.active().get(pk=int(data["product"]))
    except (ValueError, KeyError, TypeError, Product.DoesNotExist):
        return JsonResponse({"error": "Unknown product."}, status=400)

    size = str(data.get("size") or "")
    if product.size_list and size not in product.size_list:
        return JsonResponse({"error": "Please choose a valid size."}, status=400)
    if not product.size_list:
        size = ""

    order = OrderRequest.objects.create(product=product, product_name=product.name, price=product.price, size=size)
    return JsonResponse({"id": order.pk}, status=201)
