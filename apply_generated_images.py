import os
import shutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from ecom.models import Product

# Generated images paths
base_dir = "/home/dipanshu/.gemini/antigravity-ide/brain/8b19a2b3-fc1a-4a4c-9452-f4bc702a3844"
iphone_img = os.path.join(base_dir, "iphone_mockup_1785339864720.png")
tv_img = os.path.join(base_dir, "lg_tv_mockup_1785339876159.png")
gift_img = os.path.join(base_dir, "gift_box_1785339887044.png")

print("Applying generated images to products...")

for p in Product.objects.all():
    if p.product_image and p.product_image.name:
        path = p.product_image.path
        
        # Apply iPhone
        if "iphone" in p.name.lower():
            shutil.copy2(iphone_img, path)
            print(f"Set iPhone image for: {p.name}")
        # Apply TV
        elif "tv" in p.name.lower():
            shutil.copy2(tv_img, path)
            print(f"Set TV image for: {p.name}")
        # Apply Gift
        elif "gift" in p.name.lower():
            shutil.copy2(gift_img, path)
            print(f"Set Gift image for: {p.name}")

print("Done applying generated images!")
