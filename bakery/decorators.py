from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def staff_required(view_func):
    """
    Decorator to require staff role for view access.
    Staff users (role='staff') and superusers can access.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if user is superuser or has staff role
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user has staff role in profile
        if hasattr(request.user, 'profile') and request.user.profile.role == 'staff':
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied("You don't have permission to access this page.")
    
    return wrapped_view

def admin_required(view_func):
    """
    Decorator to require admin role for view access.
    Only superusers can access.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view

def customer_required(view_func):
    """
    Decorator to require customer role for view access.
    Customers (role='customer') can access.
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusers and staff can also access customer pages
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'profile') and request.user.profile.role == 'customer':
            return view_func(request, *args, **kwargs)
        
        raise PermissionDenied("You don't have permission to access this page.")
    
    return wrapped_view
