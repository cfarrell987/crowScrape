from django.urls import path
from app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("track/", views.track_price, name="track_price"),
    path("item_price_graph/", views.item_price_graph, name="item_price_graph"),
    path("list_items/", views.list_items, name="list_items"),
    path("bulk_track/", views.bulk_track, name="bulk_track"),
    path(
        "get_items_by_category/",
        views.get_items_by_category,
        name="get_items_by_category",
    ),
]
