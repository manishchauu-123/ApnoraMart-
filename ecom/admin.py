from django.contrib import admin
from .models import Customer, Product, Orders, Feedback, Vendor, Category

# 👤 Customer Admin: नाम और मोबाइल लिस्ट में दिखेगा
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'mobile', 'address')
admin.site.register(Customer, CustomerAdmin)

# 📦 Product Admin: नाम, कीमत और वेंडर का नाम दिखेगा
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'vendor', 'category')
    list_filter = ('category', 'vendor') # साइड में फ़िल्टर करने का ऑप्शन
admin.site.register(Product, ProductAdmin)

# 🚚 Orders Admin: ऑर्डर की तारीख और स्टेटस दिखेगा
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'status', 'order_date', 'is_paid')
    list_editable = ('status',) # सीधे बाहर से ही स्टेटस बदल पाएंगे
admin.site.register(Orders, OrderAdmin)

# 💬 Feedback Admin
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
admin.site.register(Feedback, FeedbackAdmin)

# 📍 Vendor Admin: दुकान का नाम और लोकेशन (Lat/Lon) बाहर ही दिखेगी
class VendorAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'mobile', 'city', 'lat', 'lon', 'is_verified')
    list_filter = ('is_verified', 'state')
admin.site.register(Vendor, VendorAdmin)

# 📂 Category Admin
admin.site.register(Category)