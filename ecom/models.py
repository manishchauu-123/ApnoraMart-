from django.db import models
from django.contrib.auth.models import User

# --- 1. CUSTOMER MODEL ---
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/CustomerProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20, null=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name

# --- 2. CATEGORY MODEL ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name

# --- 3. VENDOR MODEL ---
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address_line = models.CharField(max_length=200, default='Unknown')
    city = models.CharField(max_length=50, default='Unknown')
    state = models.CharField(max_length=50, default='Unknown')
    pincode = models.CharField(max_length=6, default='000000')
    lat = models.FloatField(default=0.0, null=True, blank=True)
    lon = models.FloatField(default=0.0, null=True, blank=True)

    # KYC & Documents
    aadhar_number = models.CharField(max_length=16, null=True)
    pan_number = models.CharField(max_length=10, default='ABCDE1234F')
    aadhar_image = models.ImageField(upload_to='vendor/aadhar/', null=True, blank=True)
    pan_image = models.ImageField(upload_to='vendor/pan/', null=True, blank=True)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name

# --- 4. PRODUCT MODEL ---
class Product(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=40)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

# --- 5. ORDERS MODEL ---
class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    is_paid = models.BooleanField(default=False)

# --- 6. FEEDBACK MODEL (🔥 यहाँ बदलाव किए गए हैं 🔥) ---
class Feedback(models.Model):
    # अब फीडबैक प्रोडक्ट और कस्टमर से जुड़ा है
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    
    name = models.CharField(max_length=40) # फीडबैक देने वाले का नाम
    feedback = models.TextField(max_length=500) # रिव्यु मैसेज
    
    # आप रेटिंग भी जोड़ सकते हैं (1-5 स्टार)
    rating = models.PositiveIntegerField(default=5) 
    
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.name}"