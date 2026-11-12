from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("stationery/", views.section_page, {"section": "stationery"}, name="stationery"),
    path("fashion/", views.section_page, {"section": "fashion"}, name="fashion"),
    path("api/products/", views.api_products, name="api-products"),
    path("api/orders/", views.api_order, name="api-order"),
    # Old static-site URLs
    path("index.html", RedirectView.as_view(pattern_name="home", permanent=True)),
    path("stationery.html", RedirectView.as_view(pattern_name="stationery", permanent=True)),
    path("fashion.html", RedirectView.as_view(pattern_name="fashion", permanent=True)),
]
