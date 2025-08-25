from django.urls import path
from . import views
app_name = 'secretary' 
urlpatterns = [
    path('', views.dashboard, name='secretary_dashboard'),
    path('accept/<int:patient_id>/', views.accept_patient, name='accept_patient'),
    path('register/', views.register_patient, name='register_patient'),
    path('accept_existing_patient/', views.accept_existing_patient, name='accept_existing_patient'),
    path('profile/<str:patient_id>/', views.patient_profile, name='patient_profile'),
    path("get_last_refraction/", views.get_patient_last_refraction_t2, name="get_patient_last_refraction_t2"),
    path('remove/<int:patient_id>/', views.remove_patient, name='remove_patient'),
    path("get_last_refraction/<str:patient_id>/", views.get_patient_last_refraction, name="get_patient_last_refraction"),
    path("patients/table/", views.patients_table_partial, name="patients_table_partial"),
]
