import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from store.models import Product, Order, Customer, OrderItem, ShippingAddress
from store.utils import guestOrder


class StoreView(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            customer = self.request.user.customer
            order, created, = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
        else:
            items, order = [], {'get_cart_items': 0, 'get_cart_total': 0}
        context['items'] = items
        context['order'] = order
        return context


class IndexView(StoreView, ListView):
    template_name = 'store/store.html'
    queryset = Product.objects.all()
    context_object_name = 'products'


class CartView(StoreView, ListView):
    model = Customer
    template_name = 'store/cart.html'


class CheckOutView(StoreView, ListView):
    template_name = 'store/checkout.html'
    model = Customer


class UpdateItemView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        action = data.get('action')
        customer = request.user.customer
        order, created, = Order.objects.get_or_create(customer=customer, complete=False)
        product = Product.objects.get(id=data.get('productId'))
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()
            order, created, = Order.objects.get_or_create(customer=customer, complete=False)
        data = {
            'get_cart_items': order.get_cart_items,
            'get_cart_total': order.get_cart_total,
            'orderItem': orderItem.quantity
        }
        return JsonResponse(data, safe=False)


class ProcessOrderView(View):
    def post(self, request, *args, **kwargs):
        transaction_id = datetime.now().timestamp()
        data = request.POST

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

        return render(request, 'store/store.html', {'checkout': True})
