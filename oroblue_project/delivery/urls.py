from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),

    # Customers
    path('customers/', views.customer_list, name="customer_list"),
    path('customers/add/', views.customer_add, name="customer_add"),
    path('customers/<int:pk>/', views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    path("customers/<int:pk>/balance/edit/", views.customer_balance_edit, name="customer_balance_edit"),

    # Deliveries
    path('deliveries/', views.delivery_list, name="delivery_list"),
    path('deliveries/add/', views.delivery_add, name="delivery_add"),

    # Transactions
    path('transactions/', views.transaction_list, name="transaction_list"),
    path('transactions/add/', views.transaction_add, name="transaction_add"),

    # Bottle Price
    path('bottle-price/', views.bottle_price, name="bottle_price"),
]
