from rest_framework import serializers
from .models import ProductVariation

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ["id", "name", "slug", "code", "thumbnail", "attributes_list"]
