from secretary.models import Patient
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from doctor.models import Refraction  # model to store refraction data
from django.utils.dateparse import parse_date
from django.http import JsonResponse
# Doctor dashboard: show only accepted patients
from django.contrib.auth.decorators import login_required
@login_required
def doctor_dashboard(request):
    patients = Patient.objects.filter(status="accepted").order_by('-id')
    return render(request, "doctor/dashboard.html", {"patients": patients})


# Patient profile view
def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    last_refraction = Refraction.objects.filter(patient=patient).order_by('-created_at').first()
    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    refractions = Refraction.objects.filter(patient=patient)
    
    if start_date:
        refractions = refractions.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        refractions = refractions.filter(created_at__date__lte=parse_date(end_date))
                
    return render(request, "doctor/patient_profile.html", {
        "patient": patient,
        "last_refraction": last_refraction,
        'past_refractions': refractions.order_by('-created_at'),
    })

# Submit refraction
def submit_refraction(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == "POST":
        od = request.POST.get('od')
        os = request.POST.get('os')
        odcl=request.POST.get('odcl')
        oscl=request.POST.get('odcl')
        axis = request.POST.get('axis')  # you had this in form
        pd = request.POST.get('pd')

        Refraction.objects.create(
            patient=patient,
            od=od,
            os=os,
            odcl=odcl,
            oscl=oscl,
            axis=axis,
            pd=pd
        )

        # If AJAX → return JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Refraction saved!"})

        # If normal form submit → redirect
        return redirect('patient_profile', patient_id=patient.patient_id)

    return redirect('patient_profile', patient_id=patient.patient_id)

# Remove patient from doctor's accepted list
def remove_from_accepted(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect(request.META.get('HTTP_REFERER', 'doctor_dashboard'))
def remove_from_accepted_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect('doctor_dashboard')

# List of all patients with optional search
def doctor_patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('-id')
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(patient_id__icontains=query))
    return render(request, "doctor/patient_list.html", {"patients": patients})

# Completely delete a patient
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.delete()
    return redirect('doctor_patient_list')
