import os
import django
import urllib.request
import urllib.parse
import ssl

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from ecom.models import Product, Category

# Ignore SSL errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_image(keyword, path):
    # Get a clean keyword
    query = urllib.parse.quote(keyword)
    url = f"https://loremflickr.com/400/400/{query}/all"
    
    try:
        print(f"Fetching image for '{keyword}'...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(path, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Saved: {path}")
    except Exception as e:
        print(f"Error fetching {keyword}: {e}")

print("Fixing Product Images...")
for p in Product.objects.all():
    if p.product_image and p.product_image.name:
        path = p.product_image.path
        keyword = p.name.split()[0].lower() # e.g. "Apple" or "LG" or "Gift"
        if "iphone" in p.name.lower(): keyword = "iphone"
        elif "tv" in p.name.lower(): keyword = "television"
        fetch_image(keyword, path)

print("Fixing Category Images...")
for c in Category.objects.all():
    if c.image and c.image.name:
        path = c.image.path
        keyword = c.name.split()[0].lower()
        if "vegetable" in keyword: keyword = "vegetables"
        if "dairy" in keyword: keyword = "dairy"
        fetch_image(keyword, path)

print("Done generating realistic images!")
