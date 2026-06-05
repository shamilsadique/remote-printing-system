from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', profile, name="profile"),
    path('update_profile/', update_profile, name='update_profile'),
    path('list_orders/', list_orders, name='list_orders'),
    path('order/', order, name="order"),
    path('process_order/', process_order, name='process_order'),
    path('order_success/', order_success, name='order_success'),
    path('payment_success/', payment_success, name='payment_success'),
    path('cancel_order/<int:order_id>/', cancel_order, name='cancel_order'),
]