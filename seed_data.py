import pandas as pd
from store_manager.models import Product, ProductVariation, Category, AttributeValue


data_file_path = "./coirplus_product_import.xlsx"
data_file = pd.read_excel(data_file_path)
print(data_file.columns)

def create_product():
    for row in data_file.iterrows():
        data = row[1]
        category = Category.objects.filter(title=data["Range"]).first()
        if category:
            title = data["Variant"]
            product = Product.objects.filter(title=title).first()
            if product:
                product.categories.add(category)
                product.save()
                continue
            short_description = data["Short description"]
            description = data["Long description"]
            new_product = Product.objects.create(
                title=title,
                short_description=short_description,
                description=description,
            )
            new_product.categories.add(category)
            new_product.save()
            print(new_product)
            # print(category, title, short_description, description, sep="\n", end="\n\n")


def create_product_variation():
    for row in data_file.iterrows():
        data = row[1]
        title = data["Variant"]
        product = Product.objects.filter(title=title).first()
        if product:
            sku = data["SKU"]
            variation = ProductVariation.objects.filter(sku=sku).first()
            if variation:
                continue
            size = AttributeValue.objects.get(value=data["Size Label"])
            length = int(data['Length (inch)'])
            width = int(data['Width (inch)'])
            height = int(data['Thickness (inch)'])
            warranty = int(data['Warranty (yrs)'])
            base_price = float(data['MRP (INR)'])
            sale_price = float(data['Selling Price (INR)'])
            stock = 10
            new_variation = ProductVariation.objects.create(
                product=product,
                sku=sku,
                length=length,
                width=width,
                height=height,
                warranty=warranty,
                base_price=base_price,
                sale_price=sale_price,
                stock=stock,
            )
            new_variation.attributes.add(size)
            new_variation.save()
            print(new_variation)
            # print(product, sku, size, length, width, height, warranty, base_price, sale_price, stock)
