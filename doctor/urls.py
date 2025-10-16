
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = "doctor"

urlpatterns = [
    path('', views.doctor_dashboard, name='doctor_dashboard'),

    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path("optics/<str:patient_id>", views.optics_page, name="optics_page"),  # 👈 this gives the name
    path('profile/<str:patient_id>/', views.patient_profile, name='patient_profile'),
    path('submit_refraction/<str:patient_id>/', views.submit_refraction, name='submit_refraction'),

    path('submit_refraction/<str:patient_id>/', views.submit_refraction, name='submit_refraction'),
    path('delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('remove/<str:patient_id>/', views.remove_from_accepted, name='remove_from_accepted'),
    path('patients/', views.doctor_patient_list, name='doctor_patient_list'),
    # urls.py
    path('remove_from_accepted_profile/<str:patient_id>/', views.remove_from_accepted_profile, name='remove_from_accepted_profile'),
    
    path('patients-fragment/', views.patients_fragment, name='patients_fragment'),
    path("patient/<str:patient_id>/pdf/", views.download_summary_pdf, name="download_summary_pdf"),
    path("patient/<str:patient_id>/wait/", views.move_to_waiting, name="move_to_waiting"),  # <-- NEW
    path('patient/<str:patient_id>/save_orders/', views.save_orders, name='save_orders'),
    path('patient/<str:patient_id>/update_general_info/', views.update_general_info, name='update_general_info'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)