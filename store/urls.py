from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from store.views import IndexView, CartView, CheckOutView, UpdateItemView, ProcessOrderView

urlpatterns = [
    path('', IndexView.as_view(), name='store'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('update/', csrf_exempt(UpdateItemView.as_view()), name='update'),
    path('process_order/', ProcessOrderView.as_view(), name='process_order'),
]
