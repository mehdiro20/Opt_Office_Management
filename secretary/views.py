from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient
from doctor.models import Refraction  # adjust import if needed
from django.utils import timezone
from datetime import datetime
# Secretary dashboard: shows only waiting patients
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
def dashboard(request):
    """
    Secretary dashboard with optional filters by date and status.
    """
    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')  # "waiting", "accepted", "done" or "all"

    patients = Patient.objects.all().order_by('-id')

    # Filter by date if provided
    if start_date:
        patients = patients.filter(created_at__date__gte=start_date)
    if end_date:
        patients = patients.filter(created_at__date__lte=end_date)

    # Filter by status if provided
    if status and status != "all":
        patients = patients.filter(status=status)

    context = {
        "patients": patients,
        "start_date": start_date,
        "end_date": end_date,
        "status": status or "all",
    }
    return render(request, "secretary/dashboard.html", context)


def patients_table_partial(request):
    """
    Returns the partial patients table for AJAX refresh.
    Includes filtering by date and status.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')  # optional

    patients = Patient.objects.all().order_by('-id')

    if start_date:
        patients = patients.filter(created_at__date__gte=start_date)
    if end_date:
        patients = patients.filter(created_at__date__lte=end_date)
    if status and status != "all":
        patients = patients.filter(status=status)

    return render(request, "secretary/patients_table.html", {"patients": patients})
def accept_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.status = "accepted"
    patient.save()
    return redirect('secretary:secretary_dashboard')

# Register new patient

def register_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        family_name = request.POST.get('family_name')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        melli_code = request.POST.get('melli_code')
        reason = request.POST.get('reason')

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        def ajax_error(msg, status=400):
            return JsonResponse({'success': False, 'error': msg}, status=status)

        # Required fields
        if not all([name, family_name, age, gender, reason]):
            msg = "All required fields must be filled!"
            return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

        # Format checks
        if phone and not phone.isdigit():
            msg = "Phone number must contain digits only."
            return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

        if melli_code and not melli_code.isdigit():
            msg = "Melli code must contain digits only."
            return ajax_error(msg) if is_ajax else _redirect_with_message(request, msg, error=True)

        # Duplicate Melli code
        if melli_code and Patient.objects.filter(melli_code=melli_code).exists():
            msg = "This Melli code is already registered."
            # 409 Conflict is a good semantic status for duplicates
            return ajax_error(msg, status=409) if is_ajax else _redirect_with_message(request, msg, error=True)

        # Create
        patient = Patient.objects.create(
            name=name,
            family_name=family_name,
            phone=phone,
            age=age,
            gender=gender,
            melli_code=melli_code,
            reason=reason
        )

        msg = f"Patient {name} registered successfully."
        return JsonResponse({'success': True, 'message': msg}) if is_ajax else _redirect_with_message(request, msg)

    # For non-POST:
    return redirect('secretary:secretary_dashboard')


def _redirect_with_message(request, msg, error=False):
    if error:
        messages.error(request, msg)
    else:
        messages.success(request, msg)
    return redirect('secretary:secretary_dashboard')

def remove_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.status = 'done'  # mark as done instead of deleting
        patient.save()
    return redirect('secretary:secretary_dashboard')



# View patient profile (works for both secretary and doctor)
def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    return render(request, "doctor/patient_profile.html", {"patient": patient})

# Get last refraction of a patient
def get_patient_last_refraction(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)  # or patient_id if that's your unique field
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
def get_patient_last_refraction_t2(request):
   
        return render(request, "secretary/get_last_refraction.html")
    
def get_patient_last_refraction_t3(request):
   if request.method == 'POST':
       patient_id = request.POST.get('patient_id')
       try:
           patient = Patient.objects.get(patient_id=patient_id)  # or patient_id if that's your unique field
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
       
        
@require_POST
def accept_existing_patient(request):
    melli_code = request.POST.get("melli_code")
    if not melli_code:
        return JsonResponse({"success": False, "error": "Please provide Patient ID or Melli Code."})

    try:
        # Try to find patient by ID or Melli Code
        patient = Patient.objects.filter(melli_code=melli_code).first() or Patient.objects.filter(patient_id=melli_code).first()
        if not patient:
            return JsonResponse({"success": False, "error": "No patient found."})

        patient.status = "waiting"
        patient.save()

        return JsonResponse({"success": True, 'patient_id': patient.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})       