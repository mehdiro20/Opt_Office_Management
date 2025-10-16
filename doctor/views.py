from secretary.models import Patient
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

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
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from doctor.models import Refraction, OpticsDescription
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.shortcuts import render
from .models import Order
from .models import Register_Order

@login_required

@permission_required('doctor.view_patient', raise_exception=True)
def doctor_dashboard(request):


    return render(request, "doctor/dashboard.html")


@permission_required('doctor.view_patient', raise_exception=True)
# Patient profile view
def patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    last_refraction = Refraction.objects.filter(patient=patient).order_by('-created_at').first()
    # Date filtering
    orders = Order.objects.all()  # fetch all orders


    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    refractions = Refraction.objects.filter(patient=patient)
    role=None
    if request.user.is_authenticated:

          role = getattr(request.user, "role", None)
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
        "role":role,
        "orders":orders
    }
    context.update(patient_summary(request,patient_id))
    context.update(make_orders(request,patient_id))
    
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
        oducva= request.POST.get('oducva')
        odbcva= request.POST.get('odbcva')
        
        os = request.POST.get('os')
        osucva= request.POST.get('osucva')
        osbcva= request.POST.get('osbcva')
        odcl=request.POST.get('odcl')
        oscl=request.POST.get('oscl')
        axis = request.POST.get('axis')  # you had this in form
        pd = request.POST.get('pd')

        Refraction.objects.create(
            subject=subject,
            patient=patient,
            od=od,
            oducva=oducva,
            odbcva=odbcva,
            os=os,
            osucva=osucva,
            osbcva=osbcva,
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
def move_to_waiting(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "waiting_out"  # move back to secretary list
        patient.save()
        messages.info(request, f"⏳ Patient {patient.name} moved to waiting list.")
    return redirect('doctor:doctor_dashboard')

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
    today = timezone.localdate()  # YYYY-MM-DD
    
# Filter patients updated today (ignoring time)
    patients = Patient.objects.filter(updated_date__date=today)
    
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
    

@permission_required('doctor.view_patient', raise_exception=True)


def download_summary_pdf(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # Example: get last refraction + optics
    last_refraction = Refraction.objects.filter(patient=patient).order_by('-created_at')[:2]
    last_optics = OpticsDescription.objects.filter(patient_id=patient_id).order_by('-created_at')[:2]
    
    # Context for template
    context = {
    "patient": patient,
    "refractions": last_refraction,
    "optics": last_optics
        }
    
    # Render template
    template = get_template("doctor/patient_summary_pdf.html")  # make sure this exists!
    html = template.render(context)
    
    # Create PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="patient_{patient.patient_id}_summary.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response

@permission_required('doctor.view_patient', raise_exception=True)
@require_POST
def update_general_info(request, patient_id):
    """Update general patient info from doctor profile via AJAX."""
    try:
        patient = get_object_or_404(Patient, patient_id=patient_id)
        data = json.loads(request.body.decode("utf-8"))

        allowed_fields = ["name", "age", "gender", "phone", "email","melli_code"]
        updated_fields = []
        new_melli_code = data.get("melli_code")
        if new_melli_code and new_melli_code != patient.melli_code:
            existing_patient = Patient.objects.filter(melli_code=new_melli_code).exclude(id=patient.id).first()
            if existing_patient:
                return JsonResponse({
                    "success": False,
                    "error": f"This Melli_Code is already registered to another patient (ID: {existing_patient.patient_id})."
                }, status=409)
            
            
        new_name = data.get("name")
        if new_name and new_name != patient.name:
            existing_patient = Patient.objects.filter(name=new_name).exclude(id=patient.id).first()
            if existing_patient:
                return JsonResponse({
                    "success": False,
                    "error": f"This Name is already registered to another patient (ID: {existing_patient.patient_id})."
                }, status=409)
            
            
        melli_c = data.get("melli_code")    
        if len(str(melli_c))!=10:
           return JsonResponse({
               "success": False,
               "error":"melli code has 10 digits not more or less"
           }, status=409)
        
        for field in allowed_fields:
            if field in data and data[field] is not None:
                setattr(patient, field, data[field])
                updated_fields.append(field)

        if updated_fields:
            patient.save(update_fields=updated_fields)
        else:
            return JsonResponse({"success": False, "error": "No valid fields provided."}, status=400)

        return JsonResponse({
            "success": True,
            "message": "Patient info updated successfully!",
            "updated_fields": updated_fields
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": "str(e)"}, status=500)


@permission_required('doctor.view_patient', raise_exception=True)
def save_orders(request,patient_id):
    if request.method == "POST":
        patient_id = patient_id
        orders_data = json.loads(request.POST.get("orders_data"))
        print(orders_data)
        incoming_ids = [o["id"] for o in orders_data]

        # Delete orders that are in DB but not in the new incoming list
        Register_Order.objects.filter(patient_id=patient_id).exclude(unique_id__in=incoming_ids).delete()

        # Save each order
        for o in orders_data:
            Register_Order.objects.update_or_create(
                unique_id=o['id'],  # lookup by unique_id
                defaults={
                    'patient_id': patient_id,
                    'order_name': o['order'],
                    'duration': o['duration'],
                    'priority': o['priority'],
                }
          )
        return redirect('doctor:patient_profile', patient_id=patient_id)  # Redirect back after saving
    return redirect('doctor:patient_profile', patient_id=patient_id)


@permission_required('doctor.view_patient', raise_exception=True)
def make_orders(request, patient_id):
 
    
    # Fetch previous orders for this patient
    existing_orders = Register_Order.objects.filter(patient_id=patient_id)
    
    # Convert queryset to a list of dicts for JS
    orders_for_js = [
        {
            "id": o.unique_id,
            "order": o.order_name,
            "duration": o.duration,
            "priority": o.priority
        }
        for o in existing_orders
    ]
    
    context = {
    
        "orders_ex": existing_orders,  # For datalist if needed
        "existing_orders_json": json.dumps(orders_for_js)
    }
    return context
