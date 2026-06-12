from django.shortcuts import redirect
from django.conf import settings

class RequirePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.has_usable_password():
            # Allow access to set password page, logout, and static/admin
            allowed_paths = ['/set-password.php', '/logout.php', '/admin/', '/static/', '/media/']
            if not any(request.path.startswith(path) for path in allowed_paths):
                return redirect('set_password')
        
        response = self.get_response(request)
        return response
