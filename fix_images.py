import os
import django
from PIL import Image

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from ecom.models import Product, Category, Customer, Vendor
from django.conf import settings

# Create a generic placeholder image
dummy_image_path = os.path.join(settings.BASE_DIR, 'dummy.png')
img = Image.new('RGB', (300, 300), color = (100, 149, 237)) # Cornflower blue
img.save(dummy_image_path)

def fix_image_field(instance, field_name):
    image_field = getattr(instance, field_name)
    if image_field and image_field.name:
        path = image_field.path
        if not os.path.exists(path):
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            # Copy dummy image
            img.save(path)
            print(f"Created placeholder for: {image_field.name}")

print("Fixing Product images...")
for p in Product.objects.all():
    fix_image_field(p, 'product_image')

print("Fixing Category images...")
for c in Category.objects.all():
    fix_image_field(c, 'image')

print("All missing images have been replaced with placeholders!")
