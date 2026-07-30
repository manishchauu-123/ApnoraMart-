from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import razorpay
import io
from xhtml2pdf import pisa
from django.template.loader import get_template

from . import forms, models
from .models import Product, Category

# --- 1. HELPERS & AUTHENTICATION ---
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

def is_vendor(user):
    return user.groups.filter(name='VENDOR').exists()

def Logout(request):
    logout(request)
    return redirect('home')

def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    elif is_vendor(request.user):
        return redirect('vendor-dashboard')
    else:
        return redirect('admin-dashboard')

def adminclick_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return redirect('adminlogin')

# --- 2. LOGINS ---
def customer_login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if is_customer(user):
                    login(request, user)
                    return redirect('customer-home')
                else:
                    return render(request, 'ecom/customerlogin.html', {'form': form, 'error': 'Aap Customer nahi hain!'})
    return render(request, 'ecom/customerlogin.html', {'form': form})

def vendor_login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if is_vendor(user):
                    login(request, user)
                    return redirect('vendor-dashboard')
                else:
                    return render(request, 'ecom/vendor_login.html', {'form': form, 'error': 'Aap Vendor nahi hain!'})
    return render(request, 'ecom/vendor_login.html', {'form': form})

def admin_login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    return redirect('admin-dashboard')
                else:
                    return render(request, 'ecom/adminlogin.html', {'form': form, 'error': 'Aap Admin nahi hain!'})
    return render(request, 'ecom/adminlogin.html', {'form': form})

# --- 3. SIGNUPS ---
def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
            return redirect('customerlogin')
    return render(request, 'ecom/customersignup.html', {'userForm': userForm, 'customerForm': customerForm})

def vendor_signup_view(request):
    userForm = forms.VendorUserForm()
    vendorForm = forms.VendorForm()
    if request.method == 'POST':
        userForm = forms.VendorUserForm(request.POST)
        vendorForm = forms.VendorForm(request.POST)
        if userForm.is_valid() and vendorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            vendor = vendorForm.save(commit=False)
            vendor.user = user
            vendor.save()
            my_vendor_group = Group.objects.get_or_create(name='VENDOR')
            my_vendor_group[0].user_set.add(user)
            return redirect('vendorlogin')
    return render(request, 'ecom/vendorsignup.html', {'userForm': userForm, 'vendorForm': vendorForm})

# --- 4. PUBLIC VIEWS ---
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    product_count_in_cart = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            product_count_in_cart = len(product_ids.split('|'))
    
    if request.user.is_authenticated:
        return redirect('afterlogin')

    return render(request, 'ecom/index.html', {
        'products': products,
        'categories': categories,
        'product_count_in_cart': product_count_in_cart
    })

def search_view(request):
    query = request.GET.get('query', '')
    products = models.Product.objects.all()
    if query:
        words = query.split()
        for word in words:
            products = products.filter(Q(name__icontains=word) | Q(description__icontains=word))

    product_count_in_cart = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            product_count_in_cart = len(product_ids.split('|'))

    word = "Searched Result :"
    if request.user.is_authenticated:
        return render(request, 'ecom/customer_home.html', {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})
    return render(request, 'ecom/index.html', {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})

def category_products(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    return render(request, 'ecom/category.html', {'products': products})

def compare_products(request):
    ids = request.GET.get('ids')
    products = models.Product.objects.filter(id__in=ids.split(',')) if ids else []
    return render(request, 'ecom/compare.html', {'products': products})

def aboutus_view(request):
    return render(request, 'ecom/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name) + ' || ' + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently=False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form': sub})

def send_feedback_view(request):
    feedbackForm = forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm': feedbackForm})

# --- 5. CART SYSTEM ---
def add_to_cart_view(request, pk):
    product_ids = request.COOKIES.get('product_ids', '')
    if product_ids == "":
        product_ids = str(pk)
    else:
        product_ids = product_ids + "|" + str(pk)

    buy_now = request.GET.get('buy_now') == 'true'
    if buy_now:
        response = redirect('customer-address') if request.user.is_authenticated else redirect('customerlogin')
    else:
        response = redirect(request.META.get('HTTP_REFERER', 'customer-home'))

    response.set_cookie('product_ids', product_ids)
    product = models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')
    return response

def decrease_quantity_view(request, pk):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_list = product_ids.split('|')
            if str(pk) in product_id_list:
                product_id_list.remove(str(pk))
            
            value = "|".join(product_id_list)
            response = redirect('cart')
            if value == "":
                response.delete_cookie('product_ids')
            else:
                response.set_cookie('product_ids', value)
            return response
    return redirect('cart')

def remove_from_cart_view(request, pk):
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_list = product_ids.split('|')
            product_id_list = [pid for pid in product_id_list if pid != str(pk)]
            
            value = "|".join(product_id_list)
            response = redirect('cart')
            if value == "":
                response.delete_cookie('product_ids')
            else:
                response.set_cookie('product_ids', value)
            return response
    return redirect('cart')

def cart_view(request):
    product_count_in_cart = 0
    products = []
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_list = product_ids.split('|')
            product_count_in_cart = len(product_id_list)
            
            from collections import Counter
            counts = Counter(product_id_list)
            
            for prod_id, qty in counts.items():
                try:
                    product = models.Product.objects.get(id=int(prod_id))
                    product.quantity = qty
                    product.subtotal = product.price * qty
                    total += product.subtotal
                    products.append(product)
                except models.Product.DoesNotExist:
                    pass
    return render(request, 'ecom/cart.html', {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})

# --- 6. CUSTOMER DASHBOARD ---
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = models.Product.objects.all()
    categories = models.Category.objects.all()
    product_count_in_cart = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            product_count_in_cart = len(product_ids.split('|'))
    return render(request, 'ecom/customer_home.html', {
        'products': products,
        'categories': categories,
        'product_count_in_cart': product_count_in_cart
    })

@login_required(login_url='customerlogin')
def customer_address_view(request):
    product_in_cart = False
    product_count_in_cart = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart = True
            product_count_in_cart = len(product_ids.split('|'))

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            response = redirect('payment')
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response
    return render(request, 'ecom/customer_address.html', {'addressForm': addressForm, 'product_in_cart': product_in_cart, 'product_count_in_cart': product_count_in_cart})

@login_required(login_url='customerlogin')
def payment_view(request):
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            ids = product_ids.split('|')
            for prod_id in ids:
                try:
                    p = models.Product.objects.get(id=int(prod_id))
                    total += p.price
                except models.Product.DoesNotExist:
                    pass

    if total == 0:
        total = 500  

    amount = int(total * 100)
    display_amount = total

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, 'ecom/payment.html', {
        'payment': payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'display_amount': display_amount
    })

@login_required(login_url='customerlogin')
def payment_success_view(request):
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    signature = request.GET.get('razorpay_signature')
    direct_cod = request.GET.get('direct_cod') == 'true'

    if not direct_cod:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            })
        except:
            return HttpResponse("❌ Payment Failed")

    customer = models.Customer.objects.get(user_id=request.user.id)
    email = request.COOKIES.get('email')
    mobile = request.COOKIES.get('mobile')
    address = request.COOKIES.get('address')
    product_ids = request.COOKIES.get('product_ids')

    if product_ids:
        ids = product_ids.split('|')
        for prod_id in ids:
            try:
                product = models.Product.objects.get(id=int(prod_id))
                models.Orders.objects.create(
                    customer=customer,
                    product=product,
                    status='Pending',
                    email=email,
                    mobile=mobile,
                    address=address
                )
            except models.Product.DoesNotExist:
                pass

    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.filter(customer_id=customer)
    ordered_products = [models.Product.objects.filter(id=order.product.id) for order in orders]
    return render(request, 'ecom/my_order.html', {'data': zip(ordered_products, orders)})

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF")

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    order = models.Orders.objects.get(id=orderID)
    product = models.Product.objects.get(id=productID)
    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,
        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,
    }
    return render_to_pdf('ecom/download_invoice.html', mydict)

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, 'ecom/my_profile.html', {'customer': customer})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('my-profile')
    return render(request, 'ecom/edit_profile.html', context=mydict)

# --- 7. VENDOR DASHBOARD ---
@login_required(login_url='vendorlogin')
@user_passes_test(is_vendor)
def vendor_dashboard_view(request):
    vendor = models.Vendor.objects.get(user=request.user)
    products = models.Product.objects.filter(vendor=vendor)
    orders = models.Orders.objects.filter(product__vendor=vendor).order_by('-id')
    
    return render(request, 'ecom/vendor_dashboard.html', {
        'products': products,
        'orders': orders 
    })

# 🔥 NEW: VENDOR LOCATION UPDATE FEATURE 🔥
@login_required(login_url='vendorlogin')
@user_passes_test(is_vendor)
def update_location(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if lat and lon:
        vendor = models.Vendor.objects.get(user=request.user)
        vendor.lat = lat
        vendor.lon = lon
        vendor.save()
        messages.success(request, "Dukan ki exact location sahi se set ho gayi hai!")
    else:
        messages.error(request, "Location set karne mein dikkat aayi. Dubara koshish karein.")
        
    return redirect('vendor-dashboard')


@login_required(login_url='vendorlogin')
@user_passes_test(is_vendor)
def vendor_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            product = productForm.save(commit=False)
            vendor = models.Vendor.objects.get(user=request.user)
            product.vendor = vendor
            product.save()
            return redirect('vendor-dashboard')
    return render(request, 'ecom/vendor_add_product.html', {'productForm': productForm})

# --- 8. ADMIN DASHBOARD ---
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    customercount = models.Customer.objects.all().count()
    productcount = models.Product.objects.all().count()
    ordercount = models.Orders.objects.all().count()
    orders = models.Orders.objects.all()
    ordered_products = [models.Product.objects.filter(id=order.product.id) for order in orders]
    ordered_bys = [models.Customer.objects.filter(id=order.customer.id) for order in orders]
        
    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'data': zip(ordered_products, ordered_bys, orders),
    }
    return render(request, 'ecom/admin_dashboard.html', context=mydict)

@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, 'ecom/view_customer.html', {'customers': customers})

@login_required(login_url='adminlogin')
def delete_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')

@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request, 'ecom/admin_update_customer.html', context=mydict)

@login_required(login_url='adminlogin')
def admin_products_view(request):
    products = models.Product.objects.all()
    return render(request, 'ecom/admin_products.html', {'products': products})

@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return redirect('admin-products')
    return render(request, 'ecom/admin_add_products.html', {'productForm': productForm})

@login_required(login_url='adminlogin')
def delete_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')

@login_required(login_url='adminlogin')
def update_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    productForm = forms.ProductForm(instance=product)
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})

@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders = models.Orders.objects.all()
    ordered_products = [models.Product.objects.filter(id=order.product.id) for order in orders]
    ordered_bys = [models.Customer.objects.filter(id=order.customer.id) for order in orders]
    return render(request, 'ecom/admin_view_booking.html', {'data': zip(ordered_products, ordered_bys, orders)})

@login_required(login_url='adminlogin')
def delete_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

@login_required(login_url='adminlogin')
def update_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    orderForm = forms.OrderForm(instance=order)
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request, 'ecom/update_order.html', {'orderForm': orderForm})

@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks = models.Feedback.objects.all().order_by('-id')
    return render(request, 'ecom/view_feedback.html', {'feedbacks': feedbacks}) 
def give_feedback_view(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        feedback_msg = request.POST.get('feedback')
        rating = request.POST.get('rating')
        customer = Customer.objects.get(user_id=request.user.id)
        
        # फीडबैक सेव करना
        Feedback.objects.create(
            product=product,
            customer=customer,
            name=customer.get_name,
            feedback=feedback_msg,
            rating=rating
        )
        return redirect('my-orders') # फीडबैक देने के बाद वापस ऑर्डर्स पर भेजें
    return render(request, 'ecom/give_feedback.html', {'product': product})