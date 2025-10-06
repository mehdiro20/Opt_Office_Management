from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient
from doctor.models import Refraction
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.http import JsonResponse
from django.utils import timezone
import jdatetime
from .models import Patient


# -------------------------------
# Permission check decorator
# -------------------------------
def is_secretary_doctor_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(name__in=["secretary", "doctor"]).exists()
    )


# -------------------------------
# Secretary Dashboard
# -------------------------------
@login_required
@user_passes_test(is_secretary_doctor_admin)
def dashboard(request):
    """Secretary dashboard with optional filters by date and status."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')  # "waiting", "accepted", "done" or "all"

    patients = Patient.objects.all().order_by('-id')

    if start_date:
        patients = patients.filter(created_at__date__gte=start_date)
    if end_date:
        patients = patients.filter(created_at__date__lte=end_date)
    if status and status != "all":
        patients = patients.filter(status=status)

    context = {
        "patients": patients,
        "start_date": start_date,
        "end_date": end_date,
        "status": status or "all",
    }
    return render(request, "secretary/dashboard.html", context)


@login_required
@user_passes_test(is_secretary_doctor_admin)
def patients_table_partial(request):
    """Returns the partial patients table for AJAX refresh."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')

    patients = Patient.objects.all().order_by('-id')

    if start_date:
        patients = patients.filter(created_at__date__gte=start_date)
    if end_date:
        patients = patients.filter(created_at__date__lte=end_date)
    if status and status != "all":
        patients = patients.filter(status=status)

    return render(request, "secretary/patients_table.html", {"patients": patients})


@login_required
@user_passes_test(is_secretary_doctor_admin)
def accept_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.status = "accepted"
    patient.save()
    return redirect('secretary:secretary_dashboard')


# -------------------------------
# Register new patient
# -------------------------------
@login_required
@user_passes_test(is_secretary_doctor_admin)


def register_patient(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            dob = request.POST.get('dob')  # ✅ Directly save Jalali string (YYYY/MM/DD)
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            melli_code = request.POST.get('melli_code')
            reason = request.POST.get('reason')

            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            def ajax_error(msg, status=400):
                return JsonResponse({'success': False, 'error': msg}, status=status)

            # Required fields
            if not all([name, age, gender, reason, dob]):
                msg = "All required fields must be filled!"
                return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

            if phone and not phone.isdigit():
                msg = "Phone number must contain digits only."
                return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

            if melli_code and not melli_code.isdigit():
                msg = "Melli code must contain digits only."
                return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

            if melli_code and Patient.objects.filter(melli_code=melli_code).exists():
                msg = "This Melli code is already registered."
                return ajax_error(msg, status=409) if is_ajax else _redirect_with_message(request, msg, error=True)

            # ✅ Save Patient with Jalali DOB string
            patient = Patient.objects.create(
                name=name,
                phone=phone,
                dob=dob,     # <-- saved as "1403/07/10"
                age=age,
                gender=gender,
                melli_code=melli_code,
                reason=reason
            )

            msg = f"Patient {name} registered successfully."
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': msg,
                    'patient_id': patient.patient_id,
                    'patient_name': patient.name
                })
            else:
                return _redirect_with_message(request, msg)

        except Exception as e:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            msg = f"Error registering patient: {str(e)}"
            if is_ajax:
                return JsonResponse({'success': False, 'error': msg}, status=500)
            return _redirect_with_message(request, msg, error=True)

    return redirect('secretary:secretary_dashboard')


@login_required
@user_passes_test(is_secretary_doctor_admin)
def _redirect_with_message(request, msg, error=False):
    if error:
        messages.error(request, msg)
    else:
        messages.success(request, msg)
    return redirect('secretary:secretary_dashboard')


@login_required
@user_passes_test(is_secretary_doctor_admin)
def remove_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.status = 'done'
        patient.save()
    return redirect('secretary:secretary_dashboard')


# -------------------------------
# Patient Profile and Refraction
# -------------------------------
@login_required
@user_passes_test(is_secretary_doctor_admin)
def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    return render(request, "doctor/patient_profile.html", {"patient": patient})


@login_required
@user_passes_test(is_secretary_doctor_admin)
def get_patient_last_refraction(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        refraction = Refraction.objects.filter(patient=patient).order_by('-created_at').first()
        if refraction:
            return render(request, "secretary/get_last_refraction.html", {
                "patient": patient,
                "refraction": refraction
            })
        else:
            return render(request, "secretary/get_last_refraction.html", {"patient": patient, "not_found": True})
    except Patient.DoesNotExist:
        return render(request, "secretary/get_last_refraction.html", {"not_found": True})


@login_required
@user_passes_test(is_secretary_doctor_admin)
def get_patient_last_refraction_t2(request):
    return render(request, "secretary/get_last_refraction.html")


@login_required
@user_passes_test(is_secretary_doctor_admin)
def get_patient_last_refraction_t3(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            refraction = Refraction.objects.filter(patient=patient).order_by('-created_at').first()
            if refraction:
                return render(request, "secretary/get_last_refraction.html", {
                    "patient": patient,
                    "refraction": refraction
                })
            else:
                return render(request, "secretary/get_last_refraction.html", {"patient": patient, "not_found": True})
        except Patient.DoesNotExist:
            return render(request, "secretary/get_last_refraction.html", {"not_found": True})


# -------------------------------
# Accept existing patient
# -------------------------------
@require_POST
@login_required
@user_passes_test(is_secretary_doctor_admin)
def accept_existing_patient(request):
    melli_code = request.POST.get("melli_code")
    if not melli_code:
        return JsonResponse({"success": False, "error": "Please provide Patient ID or Melli Code."})

    try:
        patient = (
            Patient.objects.filter(melli_code=melli_code).first()
            or Patient.objects.filter(patient_id=melli_code).first()
        )
        if not patient:
            return JsonResponse({"success": False, "error": "No patient found."})

        patient.status = "waiting"
        patient.save()
        return JsonResponse({"success": True, 'patient_id': patient.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# -------------------------------
# PDF Export
# -------------------------------
