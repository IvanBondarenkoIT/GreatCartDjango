from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import Cart, CartItem
from store.models import Product


# Create your views here.
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    color = request.GET.get('color')
    size = request.GET.get('size')

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


def remove_cart(request, product_id):
    _cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=_cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart")


def remove_cart_item(request, product_id):
    _cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=_cart)
    cart_item.delete()

    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        _cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=_cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.quantity * cart_item.product.price
            quantity += cart_item.quantity
        tax = (total * 10) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "store/cart.html", context=context)
