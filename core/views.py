from django.shortcuts import render


def dashboard_view(request):
    # This will render your homepage or a central dashboard
    return render(request, 'core/home.html')