from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from store.models import Product, ProductGallery


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")

    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    page_products = paginator.get_page(page)

    product_count = products.count()

    context = {
        "products": page_products,
        "product_count": product_count,
    }
    return render(request, "store/store.html", context=context)


def product_detail(request, category_slug, product_slug):
    # product = get_object_or_404(Product, slug=product_slug)
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()

    except Exception as error:
        raise error

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "product_gallery": product_gallery,
    }

    return render(request, "store/product_detail.html", context=context)


def search(request):
    products = None
    product_count = 0
    if "keyword" in request.GET:
        keyword = request.GET.get("keyword")
        if keyword:
            products = Product.objects.order_by("-created_date").filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()

    context = {"products": products, "product_count": product_count}
    return render(request, "store/store.html", context=context)
