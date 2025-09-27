from secretary.models import Patient
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from doctor.models import Refraction  # model to store refraction data
from django.utils.dateparse import parse_date
from django.http import JsonResponse
# Doctor dashboard: show only accepted patients
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib.auth.decorators import permission_required
from doctor.models import BrandsSplenss
from doctor.models import OpticsFeature

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from doctor.models import Refraction, OpticsDescription
from django.contrib import messages
from django.utils import timezone





@login_required

@permission_required('doctor.view_patient', raise_exception=True)
def doctor_dashboard(request):
    patients = Patient.objects.filter(status="accepted").order_by('-id')
    return render(request, "doctor/dashboard.html", {"patients": patients})


@permission_required('doctor.view_patient', raise_exception=True)
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
    splens = BrandsSplenss.objects.all()                
    optics_features = OpticsFeature.objects.all()

    
    context= {
        "patient": patient,
        "last_refraction": last_refraction,
        'past_refractions': refractions.order_by('-created_at'),
        "MEDIA_URL": settings.MEDIA_URL,
        "splenss": splens,
        "optics_features": optics_features,

    }
    context.update(patient_summary(request,patient_id))

    
    return render(request, "doctor/patient_profile.html",context)


def get_patient_data(patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    last_optics_desc = OpticsDescription.objects.filter(patient_id=patient_id).order_by('-created_at').first()
    
    return {'last_optics_desc': last_optics_desc}

@permission_required('doctor.view_patient', raise_exception=True)
# Submit refraction
def submit_refraction(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == "POST":
        subject=request.POST.get('subject')
        od = request.POST.get('od')
        os = request.POST.get('os')
        odcl=request.POST.get('odcl')
        oscl=request.POST.get('oscl')
        axis = request.POST.get('axis')  # you had this in form
        pd = request.POST.get('pd')

        Refraction.objects.create(
            subject=subject,
            patient=patient,
            od=od,
            os=os,
            odcl=odcl,
            oscl=oscl,
         
            pd=pd
        )

        # If AJAX → return JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Refraction saved!"})

        # If normal form submit → redirect
        return redirect('patient_profile', patient_id=patient.patient_id)

    return redirect('patient_profile', patient_id=patient.patient_id)
@permission_required('doctor.view_patient', raise_exception=True)
# Remove patient from doctor's accepted list
def remove_from_accepted(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect(request.META.get('HTTP_REFERER', 'doctor:doctor_dashboard'))
@permission_required('doctor.view_patient', raise_exception=True)
def remove_from_accepted_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect('doctor:doctor_dashboard')
@permission_required('doctor.view_patient', raise_exception=True)
# List of all patients with optional search
def doctor_patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('-id')
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(patient_id__icontains=query))
    return render(request, "doctor/patient_list.html", {"patients": patients})

@permission_required('doctor.view_patient', raise_exception=True)
# Completely delete a patient
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        patient.delete()
    return redirect('doctor:doctor_dashboard')

@permission_required('doctor.view_patient', raise_exception=True)
def patients_fragment(request):
    patients = Patient.objects.filter(status='accepted')  # or whatever your filter is
    return render(request, 'doctor/patients_list.html', {'patients': patients})

@permission_required('doctor.view_patient', raise_exception=True)
def optics_page(request, patient_id):
    if request.method == "POST":
        try:
            features = request.POST.getlist("optics_features")
            brand_name = request.POST.get("brand_name", "")
            brand_material = request.POST.get("brand_material", "")
            brand_color = request.POST.get("brand_color", "")
            brand_coating = request.POST.get("brand_coating", "")
            final_description = request.POST.get("final_description", "")

            # Save to DB here...
            # patient = Patient.objects.get(patient_id=patient_id)
            OpticsDescription.objects.create(patient_id= patient_id,
                                             description=final_description
                                             
                                                 
                                             
                                             
                                             )

            messages.success(request, "✅ Optics saved successfully!")
            return redirect("doctor:patient_profile", patient_id=patient_id)

        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")
            return redirect("doctor:patient_profile", patient_id=patient_id)

    return redirect("doctor:patient_profile", patient_id=patient_id)


@permission_required('doctor.view_patient', raise_exception=True)
def patient_summary(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # defaults
    rows = request.session.get("rows", 1)
    include_refraction = request.session.get("include_refraction", False)
    include_optics = request.session.get("include_optics", False)

    if request.method == "POST":
        # read values from form
        rows = int(request.POST.get("rows", 1))
        include_refraction = "include_refraction" in request.POST
        include_optics = "include_optics" in request.POST

        # save them in session
        request.session["rows"] = rows
        request.session["include_refraction"] = include_refraction
        request.session["include_optics"] = include_optics

    refractions = None
    optics = None

    if include_refraction:
        refractions = Refraction.objects.filter(patient=patient).order_by("-created_at")[:rows]

    if include_optics:
        optics = OpticsDescription.objects.filter(patient_id=patient_id).order_by("-created_at")[:rows]

    context = {
        "patient": patient,
        "rows": rows,
        "include_refraction": include_refraction,
        "include_optics": include_optics,
        "refractions": refractions,
        "optics": optics,
    }
    return context
