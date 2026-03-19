from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from .models import Product, Review


def update_product_rating(sender, instance, add=True, **kwargs):
    product = instance.product
    rating = instance.rating
    # old rating
    rated_stars = product.ratings.get("rated_stars", 0)
    reviews_count = product.ratings.get("reviews_count", 0)
    # rew rating
    if add:
        rated_stars += instance.rating
        reviews_count += 1
    else:
        rated_stars -= instance.rating
        reviews_count -= 1
    total_stars = reviews_count * 5
    try:
        avg_rating = rated_stars / reviews_count
    except ZeroDivisionError:
        avg_rating = 0
    product.ratings = {
        "avg_rating": round(avg_rating, 2),
        "rated_stars": rated_stars,
        "total_stars": total_stars,
        "reviews_count": reviews_count,
    }
    product.save(update_fields=["ratings"])


@receiver(post_save, sender=Product)
def update_price_range(sender, instance, **kwargs):
    updated_fields = ["price_range", "ratings"]
    if kwargs.get('update_fields') and ([item in kwargs["update_fields"] for item in updated_fields]):
        return
    print("triggered")
    variations = instance.product_variations.all()
    price_list = set()
    for variation in variations:
        price_list.add(variation.sale_price or variation.base_price)
    price_list = sorted(price_list)
    if price_list:
        instance.price_range = {
            "min": float(price_list[0]),
            "max": float(price_list[-1]),
        }
    else:
        instance.price_range = {}
    instance.save(update_fields=["price_range"])


@receiver(post_save, sender=Review)
def add_product_rating(sender, instance, **kwargs):
    update_product_rating(sender, instance, **kwargs)


@receiver(pre_delete, sender=Review)
def remove_product_rating(sender, instance, **kwargs):
    update_product_rating(sender, instance, add=False, **kwargs)
