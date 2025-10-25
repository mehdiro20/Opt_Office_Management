# accounts/views.py

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from functools import wraps
from django.contrib.auth.decorators import login_required

# -------------------------------
# Role-based decorator
# -------------------------------
def role_required(check_func, message="Unauthorized"):
    """Restrict access to users with specific roles (groups)."""
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

# -------------------------------
# Role check functions (group-based)
# -------------------------------
def is_doctor(user):
    return user.groups.filter(name="doctor").exists()

def is_secretary(user):
    return user.groups.filter(name="secretary").exists()

# -------------------------------
# Ensure groups exist (run once)
# -------------------------------
def create_groups():
    Group.objects.get_or_create(name="doctor")
    Group.objects.get_or_create(name="secretary")

# -------------------------------
# Login view
# -------------------------------
def login_view(request):
    # Ensure groups exist
    create_groups()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        redirect_url = "/"
        if user:
            login(request, user)

            # Redirect based on role
            if is_doctor(user):
                redirect_url = "/doctor/"
            elif is_secretary(user):
                redirect_url = "/secretary/"

            # AJAX request
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            else:
                return redirect(redirect_url)

        return JsonResponse({"success": False, "message": "Invalid username or password"}, status=400)

    # GET request → render login page
    return render(request, "accounts/login.html")

# -------------------------------
# Logout view
# -------------------------------
def logout_view(request):
    logout(request)
    return redirect("accounts:login")

# -------------------------------
# Doctor dashboard
# -------------------------------
@login_required(login_url='/accounts/login/')
@role_required(is_doctor, message="Only doctors can access this dashboard")
def doctor_dashboard(request):
    return render(request, "doctor/dashboard.html")

# -------------------------------
# Secretary dashboard
# -------------------------------
@login_required(login_url='/accounts/login/')
@role_required(is_secretary, message="Only secretaries can access this dashboard")
def secretary_dashboard(request):
    return render(request, "secretary/dashboard.html")

# -------------------------------
# Optional: Auto-assign group when creating a user
# -------------------------------
def create_user_with_role(username, password, role):
    """
    Create a user and assign them to 'doctor' or 'secretary' group.
    """
    create_groups()  # Ensure groups exist
    user = User.objects.create_user(username=username, password=password)
    if role == "doctor":
        group = Group.objects.get(name="doctor")
    elif role == "secretary":
        group = Group.objects.get(name="secretary")
    else:
        return user  # no group
    user.groups.add(group)
    user.save()
    return user
