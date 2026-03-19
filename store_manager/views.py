from django.shortcuts import render
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.http.response import HttpResponse

from .models import ProductVariation, Product, Review
from .forms import ReviewForm

# from faker import Faker
# faker = Faker()

# def generate_reviews(user=None, product=None, n:int = 10):
#     data = []
#     for _ in range(n):
#         data.append({
#             "user": user if user else faker.user_name(),
#             "product": product,
#             "rating": faker.random_int(1,5),
#             "title": faker.text(max_nb_chars=50),
#             "comment": faker.paragraph(nb_sentences=3),
#             "date_created": faker.past_datetime(),
#             "date_updated": faker.past_datetime(),
#         })
#     return data
# reviews = generate_reviews(n=20)


# Create your views here.
def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variation_id = request.GET.get("vid")
    if variation_id is None:
        first_variation = product.product_variations.first()
        variation_id = first_variation.id if first_variation else None
    variation = get_object_or_404(ProductVariation, product=product, id=variation_id)
    context = {
        "product": product,
        "variation": variation,
        "review_form": ReviewForm(),
        "product_reviews": product.reviews.all(),
    }
    return TemplateResponse(request, "store_manager/product_page.html", context=context)


# APIs
def get_product_variation_price(request, variation_id):
    variation = get_object_or_404(ProductVariation, id=variation_id)
    context = {
        "variation": variation
    }
    return TemplateResponse(request, "components/product_variation_price.html", context=context)


@api_view(["POST"])
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    review_form = ReviewForm(request.POST)
    if review_form.is_valid():
        Review.objects.create(
            user=request.user,
            product=product,
            title=review_form.cleaned_data["title"],
            comment=review_form.cleaned_data["comment"],
            rating=review_form.cleaned_data["rating"],
        )
        context = {
            "product": product,
            "review_form": ReviewForm(),
            "review_added": True,
        }
        response = TemplateResponse(request, "components/review_form.html", context=context)
        response["HX-Trigger"] = "refreshReviews"
        return response
    else:
        context = {
            "product": product,
            "review_form": ReviewForm(request.POST)
        }
        return TemplateResponse(request, "components/review_form.html", context=context)


@api_view(["GET"])
def get_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        "product": product,
        "product_reviews": product.reviews.all(),
    }
    return TemplateResponse(request, "components/reviews.html", context=context)


@api_view(["DELETE"])
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user == request.user:
        # pass
        review.delete()
    response = HttpResponse()
    response["HX-Trigger"] = "refreshReviews"
    return response