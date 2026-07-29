import os
import shutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from ecom.models import Category

src = "/home/dipanshu/.gemini/antigravity-ide/brain/8b19a2b3-fc1a-4a4c-9452-f4bc702a3844/clothes_category_icon_1785340997102.png"

for cat in Category.objects.all():
    if "cloth" in cat.name.lower():
        if cat.image and cat.image.name:
            dest = cat.image.path
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            print(f"Applied clothes image to: {cat.name} → {dest}")
        else:
            print(f"Category '{cat.name}' has no image path set.")

print("Done!")
