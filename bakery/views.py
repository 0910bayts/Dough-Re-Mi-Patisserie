import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.core.paginator import Paginator

from bakery.models import Product, CartItem, Order, Receipt, UserProfile, AuditLog
from bakery.forms import SignUpForm, DeliveryForm, StaffCreateForm, StaffEditForm, ProductForm, OrderStatusForm
from bakery.decorators import staff_required, admin_required

def index_view(request):
    featured_products = Product.objects.all()[:3]
    gallery_products = Product.objects.all()[:6]
    return render(request, 'index.html', {
        'featured_products': featured_products,
        'gallery_products': gallery_products
    })

def aboutus_view(request):
    return render(request, 'aboutus.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.username = form.cleaned_data['email']  # Use email as username
            user.save()
            
            UserProfile.objects.create(
                user=user,
                contactnumber=form.cleaned_data['contactnumber'],
                role='customer'  # Set default role to customer
            )
            
            # Auto log in user
            user = authenticate(username=user.username, password=form.cleaned_data['password'])
            if user is not None:
                auth_login(request, user)
            
            messages.success(request, "Signup successful!")
            return redirect('index')
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(error)
            error_msg = " ".join(errors)
            messages.error(request, error_msg)
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.is_superuser:
            return redirect('/admin/')
        elif hasattr(request.user, 'profile'):
            if request.user.profile.role == 'staff':
                return redirect('staff_dashboard')
            elif request.user.profile.role == 'customer':
                return redirect('index')
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            
            # Redirect based on role
            if user.is_superuser:
                return redirect('/admin/')
            elif hasattr(user, 'profile'):
                if user.profile.role == 'staff':
                    return redirect('staff_dashboard')
                elif user.profile.role == 'customer':
                    return redirect('index')
            return redirect('index')
        else:
            messages.error(request, "Incorrect Username or Password!")
            
    return render(request, 'login.html')

def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('index')

def menu_view(request):
    products = Product.objects.filter(is_available=True)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'menu.html', {'page_obj': page_obj, 'products': page_obj})

@login_required
def cart_get(request):
    cart_items = CartItem.objects.filter(user=request.user)
    items = []
    total_price = 0.00
    for item in cart_items:
        subtotal = float(item.product.price) * item.quantity
        items.append({
            'item_name': item.product.name,
            'item_price': float(item.product.price),
            'quantity': item.quantity,
            'subtotal': subtotal
        })
        total_price += subtotal
    
    request.session['total_price'] = str(total_price)
    return JsonResponse({'items': items, 'total_price': total_price})

@login_required
@require_POST
def cart_add(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        product = get_object_or_404(Product, name=name)
        
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        return JsonResponse({'message': 'Item added to cart'})
    except Exception as e:
        return JsonResponse({'message': f'Error adding item to cart: {str(e)}'}, status=400)

@login_required
@require_POST
def cart_remove(request):
    try:
        data = json.loads(request.body)
        index = data.get('index')
        
        cart_items = list(CartItem.objects.filter(user=request.user).order_by('id'))
        
        if 0 <= index < len(cart_items):
            item_to_remove = cart_items[index]
            if item_to_remove.quantity > 1:
                item_to_remove.quantity -= 1
                item_to_remove.save()
            else:
                item_to_remove.delete()
            return JsonResponse({'message': 'Item removed from cart'})
        else:
            return JsonResponse({'message': 'Item not found in cart'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'Error removing item from cart: {str(e)}'}, status=400)

@login_required
@require_POST
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return JsonResponse({'success': False, 'message': 'You need to add an item first!'})
        
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        
    request.session['checkout_session_id'] = session_id
    
    total_price = 0.00
    for item in cart_items:
        subtotal = item.product.price * item.quantity
        total_price += subtotal
        
        for _ in range(item.quantity):
            Order.objects.create(
                user=request.user,
                session_id=session_id,
                item_name=item.product.name,
                item_price=item.product.price
            )
            
    request.session['total_price'] = str(total_price)
    cart_items.delete()
    
    return JsonResponse({'success': True})

@login_required
def delivery_view(request):
    session_id = request.session.get('checkout_session_id')
    total_price = request.session.get('total_price', '0.00')
    
    if not session_id or not Order.objects.filter(session_id=session_id).exists():
        messages.error(request, "No active order to bill.")
        return redirect('menu')
        
    if request.method == 'POST':
        form = DeliveryForm(request.POST)
        if form.is_valid():
            Receipt.objects.create(
                user=request.user,
                session_id=session_id,
                total_price=float(total_price),
                housenumber=str(form.cleaned_data['houseNumber']),
                streetname=form.cleaned_data['street'],
                barangay=form.cleaned_data['barangay'],
                postalcode=str(form.cleaned_data['postalCode']),
                city=form.cleaned_data['city']
            )
            return redirect('receipt')
        else:
            messages.error(request, "Invalid form data. Please verify all inputs.")
    else:
        form = DeliveryForm()
        
    return render(request, 'delivery.html', {
        'form': form,
        'total_price': total_price
    })

@login_required
def receipt_view(request):
    session_id = request.session.get('checkout_session_id')
    if not session_id:
        return redirect('menu')
        
    receipt = get_object_or_404(Receipt, session_id=session_id, user=request.user)
    orders = Order.objects.filter(session_id=session_id, user=request.user)
    
    profile = getattr(request.user, 'profile', None)
    contact_number = profile.contactnumber if profile else 'Not Provided'
    
    return render(request, 'receipt.html', {
        'receipt': receipt,
        'orders': orders,
        'contact_number': contact_number
    })

@login_required
def set_password_view(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password set successfully! You can now log in using your email and password.")
            return redirect('index')
    else:
        form = SetPasswordForm(request.user)
    
    return render(request, 'set_password.html', {'form': form})

# Staff Dashboard Views
@staff_required
def staff_dashboard(request):
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    ready_orders = Order.objects.filter(status='ready').count()
    completed_orders = Order.objects.filter(status='completed').count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'ready_orders': ready_orders,
        'completed_orders': completed_orders,
    }
    return render(request, 'staff/dashboard.html', context)

@staff_required
def staff_products(request):
    products = Product.objects.all().order_by('name')
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'staff/products.html', {'page_obj': page_obj})

@staff_required
def staff_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            # Log audit
            AuditLog.objects.create(
                user=request.user,
                action='product_create',
                description=f"Created product: {product.name}",
                product_id=product.id,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Product created successfully!")
            return redirect('staff_products')
    else:
        form = ProductForm()
    
    return render(request, 'staff/product_form.html', {'form': form, 'title': 'Add Product'})

@staff_required
def staff_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Handle image upload separately
        form_data = request.POST.copy()
        if 'image' not in request.FILES:
            # Keep existing image if no new image uploaded
            form_data['image'] = product.image
        form = ProductForm(form_data, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Log audit
            AuditLog.objects.create(
                user=request.user,
                action='product_edit',
                description=f"Edited product: {product.name}",
                product_id=product.id,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Product updated successfully!")
            return redirect('staff_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'staff/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})

@staff_required
def staff_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='product_delete',
            description=f"Deleted product: {product_name}",
            product_id=product_id,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, "Product deleted successfully!")
        return redirect('staff_products')
    
    return render(request, 'staff/product_confirm_delete.html', {'product': product})

@staff_required
def staff_orders(request):
    orders = Order.objects.all().select_related('user').order_by('-ordered_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'staff/orders.html', {'page_obj': page_obj})

@staff_required
def staff_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            form.save()
            # Log audit
            AuditLog.objects.create(
                user=request.user,
                action='order_status_update',
                description=f"Updated order {order.id} status from {old_status} to {order.status}",
                order_id=order.id,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Order status updated successfully!")
            return redirect('staff_orders')
    else:
        form = OrderStatusForm(instance=order)
    
    return render(request, 'staff/order_detail.html', {'order': order, 'form': form})

# Admin Views for Staff Management
@admin_required
def admin_staff_list(request):
    staff_users = User.objects.filter(profile__role='staff').select_related('profile')
    
    return render(request, 'admin/staff_list.html', {'staff_users': staff_users})

@admin_required
def admin_staff_create(request):
    if request.method == 'POST':
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log audit
            AuditLog.objects.create(
                user=request.user,
                action='staff_create',
                description=f"Created staff account: {user.email}",
                target_user_id=user.id,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "Staff account created successfully!")
            return redirect('admin_staff_list')
    else:
        form = StaffCreateForm()
    
    return render(request, 'admin/staff_form.html', {'form': form, 'title': 'Create Staff Account'})

@admin_required
def admin_staff_edit(request, user_id):
    user = get_object_or_404(User, id=user_id, profile__role='staff')
    
    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=user)
        if form.is_valid():
            old_active = user.profile.is_active
            form.save()
            # Log audit
            action = 'staff_activate' if form.cleaned_data['is_active'] and not old_active else 'staff_deactivate'
            if old_active != form.cleaned_data['is_active']:
                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    description=f"{'Activated' if form.cleaned_data['is_active'] else 'Deactivated'} staff account: {user.email}",
                    target_user_id=user.id,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            messages.success(request, "Staff account updated successfully!")
            return redirect('admin_staff_list')
    else:
        form = StaffEditForm(instance=user)
    
    return render(request, 'admin/staff_form.html', {'form': form, 'title': 'Edit Staff Account', 'user': user})

@admin_required
def admin_staff_delete(request, user_id):
    user = get_object_or_404(User, id=user_id, profile__role='staff')
    
    if request.method == 'POST':
        user_email = user.email
        user.delete()
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='staff_deactivate',
            description=f"Deleted staff account: {user_email}",
            target_user_id=user_id,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, "Staff account deleted successfully!")
        return redirect('admin_staff_list')
    
    return render(request, 'admin/staff_confirm_delete.html', {'user': user})
