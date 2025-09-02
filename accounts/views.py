from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from functools import wraps
from django.contrib.auth.decorators import login_required
# -------- Role-based decorator for dashboards --------
def role_required(check_func, message="Unauthorized"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"success": False, "message": "Login required"}, status=401)
            if not check_func(request.user):
                return JsonResponse({"success": False, "message": message}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# -------- Login view --------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)

            # Always redirect doctors to /doctor/
            redirect_url = "/doctor/"

            # If AJAX request, return JSON
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            else:
                return redirect(redirect_url)

        # Wrong credentials → return JSON error
        return JsonResponse({"success": False, "message": "Invalid username or password"}, status=400)

    # GET → render login page
    return render(request, "accounts/login.html")

# -------- Logout view --------
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# -------- Dashboards (JSON) --------
@login_required(login_url='/accounts/login/')
#@role_required(lambda u: not u.is_staff and not u.is_superuser)
def doctor_dashboard(request):
    return render(request, '/doctor/l')