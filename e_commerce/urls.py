from django.urls import path

from . import views

urlpatterns = [
    path("items/", views.ItemListCreateAPIView.as_view()),
    path("items/<int:pk>", views.ItemRetrieveUpdateDestroyAPIView.as_view()),
    path("categories/", views.CategoryListCreateAPIView.as_view()),
    path("categories/<int:pk>", views.CategoryRetrieveUpdateDestroyAPIView.as_view()),
    path("wishlist/", views.WishlistRetrieveCreateUpdateAPIView.as_view()),
    path("cart/", views.CartRetrieveCreateUpdateAPIView.as_view()),
    path("order/<int:pk>", views.OrderRetrieveUpdateAPIView.as_view()),
    path("order/", views.OrderListCreateAPIView.as_view()),
]
