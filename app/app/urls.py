from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path("track/", views.track_price, name="track_price"),
    path("item_price_graph/", views.item_price_graph, name='item_price_graph'),
]