from django.shortcuts import render, redirect

from carts.models import Cart, CartItem
from store.models import Product


# Create your views here.
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    # get the product
    product = Product.objects.get(id=product_id)
    try:
        # get the cart using the cart_id present in the session

        _cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        _cart = Cart.objects.create(cart_id=_cart_id(request))

    _cart.save()

    try:
        _cart_item = CartItem.objects.get(product=product, cart=_cart)
        _cart_item.quantity += 1
    except CartItem.DoesNotExist:
        _cart_item = CartItem.objects.create(product=product, cart=_cart, quantity=1)

    _cart_item.save()

    return redirect("cart")


def cart(request):
    return render(request, "store/cart.html")
