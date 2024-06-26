from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from carts.models import Cart, CartItem
from store.models import Product, Variations


# Create your views here.
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []

    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            print(key, value)

            try:
                variation = Variations.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)

            except:
                pass

    try:
        _cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        _cart = Cart.objects.create(cart_id=_cart_id(request))

    _cart.save()

    is_cart_item_exist = CartItem.objects.filter(product=product, cart=_cart).exists()

    if is_cart_item_exist:
        _cart_item = CartItem.objects.filter(product=product, cart=_cart)
        # existing_variations -> database
        # current_variation -> product_variation
        # item_id -> database
        exist_variation_list = []
        cart_item_id_list = []
        for item in _cart_item:
            existing_variation = item.variations.all()
            exist_variation_list.append(list(existing_variation))
            cart_item_id_list.append(item.id)

        print(exist_variation_list)

        if product_variation in exist_variation_list:
            # increase the cart item quantity
            index = exist_variation_list.index(product_variation)
            item_id = cart_item_id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1

        else:
            # create a new cart item
            item = CartItem.objects.create(product=product, quantity=1, cart=_cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)

        item.save()

    else:
        _cart_item = CartItem.objects.create(product=product, cart=_cart, quantity=1)

        if len(product_variation) > 0:
            _cart_item.variations.clear()
            _cart_item.variations.add(*product_variation)
        _cart_item.save()

    return redirect("cart")


def remove_cart(request, product_id, cart_item_id):

    _cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=_cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass

    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    _cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=_cart, id=cart_item_id)
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

def checkout(request, total=0, quantity=0, cart_items=None):
    return render(request, "store/checkout.html")