from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Q
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.contrib import messages
from django.utils import timezone

import json
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from itertools import chain
from collections import defaultdict

from xhtml2pdf import pisa

# Models
from doctor.models import (
    BrandsSplenss,
    OpticsFeature,
    Refraction,
    OpticsDescription,
)

from .models import (
    Order,
    Register_Order,
    ImpMenuParts,
    Patient,
    GH_HealthCondition,
    GH_Medication,
    GH_Allergies,
    GH_FamilialHistory,
    GH_GeneticalHistory,
    GH_LifestyleHistory,
    GH_OcularHistory,
    GeneralHealthRecord,
    SelectedSpectacleLens,
    LensPowerRange,
    SpectacleLens
)




def is_doctor_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(name__in=["doctor"]).exists()
    )

@login_required
@user_passes_test(is_doctor_admin)
def doctor_dashboard(request):


    return render(request, "doctor/dashboard.html")

@login_required
@user_passes_test(is_doctor_admin)
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
    context.update(make_refs(request,patient_id))
    context.update(general_health_view(request,patient_id))
    context.update(general_health_patient_view(request,patient_id))
    context.update(record_imp_menu_view(request,patient_id))
    
    
    return render(request, "doctor/patient_profile.html",context)

@login_required
@user_passes_test(is_doctor_admin)
def get_patient_data(patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    last_optics_desc = OpticsDescription.objects.filter(patient_id=patient_id).order_by('-created_at').first()
    
    return {'last_optics_desc': last_optics_desc}

@login_required
@user_passes_test(is_doctor_admin)
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
        refraction_id = request.POST.get('refraction_id')
        odkmax=request.POST.get('odkmax')
        odkmin=request.POST.get('odkmin')
        oskmax=request.POST.get('oskmax')
        oskmin=request.POST.get('oskmin')
        print(refraction_id)
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
            refraction_id=refraction_id,
            pd=pd,
            odkmax=odkmax,
            odkmin=odkmin,
            oskmax=oskmax,
            oskmin=oskmin
        )

        # If AJAX → return JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "message": "Refraction saved!"})

        # If normal form submit → redirect
        return redirect('patient_profile', patient_id=patient.patient_id)

    return redirect('patient_profile', patient_id=patient.patient_id)
@login_required
@user_passes_test(is_doctor_admin)
# Remove patient from doctor's accepted list
def remove_from_accepted(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect(request.META.get('HTTP_REFERER', 'doctor:doctor_dashboard'))
@login_required
@user_passes_test(is_doctor_admin)
def move_to_waiting(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "waiting_out"  # move back to secretary list
        patient.save()
        messages.info(request, f"⏳ Patient {patient.name} moved to waiting list.")
    return redirect('doctor:doctor_dashboard')

@login_required
@user_passes_test(is_doctor_admin)
def remove_from_accepted_profile(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.method == "POST":
        patient.status = "done"  # move back to secretary list
        patient.save()
    return redirect('doctor:doctor_dashboard')
@login_required
@user_passes_test(is_doctor_admin)
# List of all patients with optional search
def doctor_patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('-id')
    
    
    if query:
        patients = patients.filter(Q(name__icontains=query) | Q(patient_id__icontains=query))
    return render(request, "doctor/patient_list.html", {"patients": patients})

@login_required
@user_passes_test(is_doctor_admin)
# Completely delete a patient
def delete_patient(request, patient_id):
 
    patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == "POST":
        patient.delete()
    return redirect('doctor:doctor_dashboard')

@login_required
@user_passes_test(is_doctor_admin)
def patients_fragment(request):
    today = timezone.localdate()  # YYYY-MM-DD
    
# Filter patients updated today (ignoring time)
    patients = Patient.objects.filter(updated_date__date=today)
    accepted_count = patients.filter(status='accepted').count()
    waiting_count = patients.filter(status='waiting_out').count()
    done_count = patients.filter(status='done').count()
    context={'patients': patients,
             'accepted_count':accepted_count,
             'waiting_count':waiting_count,
             'done_count':done_count
             }
    
    return render(request, 'doctor/patients_list.html',context)

@login_required
@user_passes_test(is_doctor_admin)
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
@login_required
@user_passes_test(is_doctor_admin)
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
    
@login_required
@user_passes_test(is_doctor_admin)


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
@login_required
@user_passes_test(is_doctor_admin)
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

@login_required
@user_passes_test(is_doctor_admin)
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

@login_required
@user_passes_test(is_doctor_admin)
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

@login_required
@user_passes_test(is_doctor_admin)
def make_refs(request, patient_id):
 
    
    # Fetch previous orders for this patient
    existing_ref = Refraction.objects.filter(patient_id=patient_id)
    
    # Convert queryset to a list of dicts for JS
    orders_for_js = [
        {
            "ref_id": o.refraction_id,
            "ref_subj": o.subject,
            "ref_od": o.od,
            "ref_os": o.os,
            "ref_pd":o.pd,
            "ref_odkmax":o.odkmax,
            "ref_odkmin":o.odkmin,
            "ref_oskmax":o.oskmax,
            "ref_oskmin":o.oskmin,
            "ref_addition":o.addition
        }
        for o in existing_ref
    ]
    
    context = {
    
        "ref_ex": existing_ref,  # For datalist if needed
        "existing_refs_json": json.dumps(orders_for_js)
    }
    return context
@login_required
@user_passes_test(is_doctor_admin)
def general_health_view(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    # All predefined health conditions
    health_conditions =  GH_HealthCondition.objects.all()

    medications =  GH_Medication.objects.all()

    allergies= GH_Allergies.objects.all()
    
    familial_history= GH_FamilialHistory.objects.all()
    
    genetical_history= GH_GeneticalHistory.objects.all()

    lifestyle_history= GH_LifestyleHistory.objects.all()
    
    ocular_history= GH_OcularHistory.objects.all()
    

    

    # Notes

    context = {

        'health_conditions': health_conditions,

        'medications': medications,
        
        'allergies':allergies,
        
        'familial_history':familial_history,
        
        'genetical_history':genetical_history,
        
        'lifestyle_history':lifestyle_history,
        
        'ocular_history':ocular_history,
        
    }
    return context



def split_and_strip(value):
    return [item.strip() for item in value.split(",")] if value else []
@login_required
@user_passes_test(is_doctor_admin)

def general_health_patient_view(request, patient_id):
    

    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Get the existing record if it exists, otherwise None
    try:
        record = GeneralHealthRecord.objects.get(patient=patient)
    except GeneralHealthRecord.DoesNotExist:
        record = None

    # Split comma-separated fields into lists for preselecting checkboxes
    selected_data = {
    "health_conditions": split_and_strip(record.systemic_diseases) if record else [],
    "ocular_history": split_and_strip(record.ocular_history) if record else [],
    "medications": split_and_strip(record.medications) if record else [],
    "allergies": split_and_strip(record.allergies) if record else [],
    "familial_history": split_and_strip(record.familial_history) if record else [],
    "genetical_history": split_and_strip(record.genetical_history) if record else [],
    "lifestyle_history": split_and_strip(record.lifestyle_history) if record else [],
    }
    
    
    
    # Allergies
    allergies_all = GH_Allergies.objects.filter(related_px_id__isnull=True)
    allergies_ps = GH_Allergies.objects.filter(related_px_id=patient_id)
    
    # Health Conditions
    health_conditions_all = GH_HealthCondition.objects.filter(related_px_id__isnull=True)
    health_conditions_ps = GH_HealthCondition.objects.filter(related_px_id=patient_id)
    
    # Ocular History
    ocular_history_all = GH_OcularHistory.objects.filter(related_px_id__isnull=True)
    ocular_history_ps = GH_OcularHistory.objects.filter(related_px_id=patient_id)
    
    # Medications
    medications_all = GH_Medication.objects.filter(related_px_id__isnull=True)
    medications_ps = GH_Medication.objects.filter(related_px_id=patient_id)
    
    # Familial History
    familial_history_all = GH_FamilialHistory.objects.filter(related_px_id__isnull=True)
    familial_history_ps = GH_FamilialHistory.objects.filter(related_px_id=patient_id)
    
    # Genetical History
    genetical_history_all = GH_GeneticalHistory.objects.filter(related_px_id__isnull=True)
    genetical_history_ps = GH_GeneticalHistory.objects.filter(related_px_id=patient_id)
    
    # Lifestyle History
    lifestyle_history_all = GH_LifestyleHistory.objects.filter(related_px_id__isnull=True)
    lifestyle_history_ps = GH_LifestyleHistory.objects.filter(related_px_id=patient_id)

    
    allergies = list({a.name: a for a in chain(allergies_all, allergies_ps)}.values())
    health_conditions = list({h.name: h for h in chain(health_conditions_all, health_conditions_ps)}.values())
    ocular_history = list({o.name: o for o in chain(ocular_history_all, ocular_history_ps)}.values())
    medications = list({m.name: m for m in chain(medications_all, medications_ps)}.values())
    familial_history = list({f.name: f for f in chain(familial_history_all, familial_history_ps)}.values())
    genetical_history = list({g.name: g for g in chain(genetical_history_all, genetical_history_ps)}.values())
    lifestyle_history = list({l.name: l for l in chain(lifestyle_history_all, lifestyle_history_ps)}.values())
        

    combined_allergies = list({a.name: a for a in chain(allergies_all, allergies_ps)}.values())
    

    context = {
        "patient": patient,
        "record": record,           
        "selected_data": selected_data,  
        "health_conditions": health_conditions,
        "ocular_history": ocular_history,
        "medications":medications,
        "allergies":allergies,
       

        "familial_history": familial_history,
        "genetical_history": genetical_history,
        "lifestyle_history": lifestyle_history,
    }

    return context


@login_required
@user_passes_test(is_doctor_admin)


def general_health_record(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == "POST":
  
        data = {
            "systemic": request.POST.get("systemic_selected", ""),
            "ocular_history": request.POST.get("ocular_history_selected", ""),
            "medications": request.POST.get("medications_selected", ""),
            "allergies": request.POST.get("allergies_selected", ""),
            "familial_history": request.POST.get("familial_history_selected", ""),
            "genetical_history": request.POST.get("genetical_history_selected", ""),
            "lifestyle_history": request.POST.get("lifestyle_history_selected", ""),
        }

        # ✅ Map section names to their respective models
        section_models = {
            "systemic": GH_HealthCondition,
            "ocular_history": GH_OcularHistory,
            "medications": GH_Medication,
            "allergies": GH_Allergies,
            "familial_history": GH_FamilialHistory,
            "genetical_history": GH_GeneticalHistory,
            "lifestyle_history": GH_LifestyleHistory,
        }

        # ✅ Create or update the General Health Record for this patient
        record, created = GeneralHealthRecord.objects.get_or_create(patient=patient)

        record.systemic_diseases = data["systemic"]
        record.ocular_history = data["ocular_history"]
        record.medications = data["medications"]
        record.allergies = data["allergies"]
        record.familial_history = data["familial_history"]
        record.genetical_history = data["genetical_history"]
        record.lifestyle_history = data["lifestyle_history"]
        record.save()

        # ✅ Ensure all selected items exist in their respective section tables
        for section, model in section_models.items():
            items = [x.strip() for x in data.get(section, "").split(",") if x.strip()]
            for item in items:
                model.objects.get_or_create(name=item, related_px_id=patient_id)

        # ✅ Redirect back to the patient profile after saving
        return redirect("doctor:patient_profile", patient_id=patient.patient_id)

    # Fallback for GET requests
    return render(request, "doctor/patient_profile.html", {"patient": patient})

@login_required
@user_passes_test(is_doctor_admin)
@require_POST
def delete_patient_item(request, patient_id, section_name):
    item_name = request.POST.get("item_name", "").strip()
    if not item_name:
        return JsonResponse({"status": "error", "message": "No item_name"})

    section_models = {
        "systemic": GH_HealthCondition,
        "ocular": GH_OcularHistory,
        "medications": GH_Medication,
        "allergies": GH_Allergies,
        "familial": GH_FamilialHistory,
        "genetical": GH_GeneticalHistory,
        "lifestyle": GH_LifestyleHistory,
    }
    model = section_models.get(section_name)
    if not model:
        return JsonResponse({"status": "error", "message": "Invalid section"})

    deleted, _ = model.objects.filter(name=item_name, related_px_id=patient_id).delete()
    if deleted:
        return JsonResponse({"status": "success"})




@login_required
@user_passes_test(is_doctor_admin)
def record_imp_menu_part(request, patient_id):
    """
    Create or update ImpMenuParts for a given patient.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST method is allowed."}, status=405)

    try:
        # Parse JSON from request body
        data = json.loads(request.body)
        important_parts = data.get('important_parts', '').strip()

        if not important_parts:
           important_parts='';

        # Get patient
        patient = get_object_or_404(Patient, patient_id=patient_id)

        # Create or update ImpMenuParts record
        imp_record, created = ImpMenuParts.objects.update_or_create(
            patient=patient,
            defaults={"imp_menu_parts": important_parts}
        )

        message = "record created successfully." if created else "record updated successfully."

        return JsonResponse({
            "success": True,
            "message": message,
            "patient_id": patient_id,
            "imp_menu_parts": imp_record.imp_menu_parts,
        })

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)
    except Patient.DoesNotExist:
        return JsonResponse({"success": False, "error": "Patient not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def record_imp_menu_view(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Get the existing ImpMenuParts record if it exists
    record = ImpMenuParts.objects.filter(patient=patient).first()  # returns None if not found

    # Preselect checkboxes
    selected_data = {
        "imp_menu_parts": split_and_strip(record.imp_menu_parts) if record else [],
    }

    context = {
        "patient": patient,
        "record_": record,  # single instance or None
        "selected_data_imp_menu_part": selected_data,  # list of strings for pre-selecting checkboxes
    }

    return context



@csrf_exempt  # if you already have csrf token in the form, this is optional
@require_POST
def rx_print(request):
    if request.method == "POST":
        rx_data_json = request.POST.get("rx_data")
        rx_data = json.loads(rx_data_json)
        # Now rx_data contains everything you sent
        return render(request, "doctor/rx_print.html", {"rx": rx_data})
    
    
@require_POST


def delete_patient_item(request, patient_id):
    if request.method == "POST":
        section = request.POST.get("section_name")
        item_name = request.POST.get("item_name")

        model_map = {
            "systemic": GH_HealthCondition,
            "ocular_history": GH_OcularHistory,
            "medications": GH_Medication,
            "allergies": GH_Allergies,
            "familial_history": GH_FamilialHistory,
            "genetical_history": GH_GeneticalHistory,
            "lifestyle_history": GH_LifestyleHistory,
        }

        model_class = model_map.get(section)
        if not model_class:
            messages.error(request, "Invalid section name.")
            return redirect("doctor:general_health_record", patient_id)

        deleted_count, _ = model_class.objects.filter(
            related_px__patient_id=patient_id, name=item_name
        ).delete()

        msg = (
            f"Item Removed from {section.replace('_', ' ').title()} section."
            if deleted_count
            else "No matching Item found for this patient."
        )
        messages.success(request, msg)

    return redirect("doctor:patient_profile", patient_id)


def add_patient_item(request, patient_id):
    if request.method == "POST":
        section = request.POST.get("section_name")
        item_name = request.POST.get("item_name")

        model_map = {
            "systemic": GH_HealthCondition,
            "ocular_history": GH_OcularHistory,
            "medications": GH_Medication,
            "allergies": GH_Allergies,
            "familial_history": GH_FamilialHistory,
            "genetical_history": GH_GeneticalHistory,
            "lifestyle_history": GH_LifestyleHistory,
        }

        model_class = model_map.get(section)
        if not model_class:
            messages.error(request, "Invalid section name.")
            return redirect("doctor:patient_profile", patient_id)

        # Check if item already exists for this patient
        existing = model_class.objects.filter(
            related_px__patient_id=patient_id, name=item_name
        ).exists()

        if existing:
            messages.warning(request, f"Item already exists in {section.replace('_', ' ').title()} section.")
        else:
            model_class.objects.create(related_px_id=patient_id, name=item_name)
            messages.success(request, f"Item added to {section.replace('_', ' ').title()} section.")

    return redirect("doctor:patient_profile", patient_id)

# views.py (inside the same app)

@require_GET
def find_lens_group(request):
    """
    Expects query params: od_sph, od_cyl, os_sph, os_cyl
    Returns JSON: { status: "no_match" } or { status: "ok", od_matches: [...], os_matches: [...] }
    Finds the nearest lens power range for each eye independently.
    """
    def parse_decimal(val):
        try:
            return Decimal(str(val))
        except (InvalidOperation, TypeError, ValueError):
            return None

    od_sph = parse_decimal(request.GET.get("od_sph"))
    od_cyl = parse_decimal(request.GET.get("od_cyl"))
    os_sph = parse_decimal(request.GET.get("os_sph"))
    os_cyl = parse_decimal(request.GET.get("os_cyl"))

    if None in (od_sph, od_cyl, os_sph, os_cyl):
        return JsonResponse({"status": "error", "message": "invalid parameters"}, status=400)
    
    qs = LensPowerRange.objects.select_related("lens", "lens__brand").all()
    
   

   

   

    def nearest_for_eye(sph, cyl):
        inside_candidates = []
    
        for r in qs:
            try:
                min_sph = Decimal(r.minus_sphere_group)
                max_sph = Decimal(r.plus_sphere_group)
                min_cyl = Decimal(r.minus_cylinder_group)
                max_cyl = Decimal(r.plus_cylinder_group)
            except (AttributeError, TypeError, InvalidOperation):
                continue
    
            if cyl == 0:
                if min_cyl != 0 or max_cyl != 0:
                    continue
            else:
                if min_cyl == 0 and max_cyl == 0:
                    continue
    
            in_sph = min_sph <= sph <= max_sph
            in_cyl = min_cyl <= cyl <= max_cyl
    
            if in_sph and in_cyl:
                range_width = (max_sph - min_sph) + (max_cyl - min_cyl)
                inside_candidates.append((range_width, r))
    
        if not inside_candidates:
            return []
    
        best_width = min(width for width, _ in inside_candidates)
        selected = [r for width, r in inside_candidates if width == best_width]
    
        results = []
        for r in selected:
            price_raw = str(getattr(r, "price", "0") or "0").replace(",", "").strip()
            try:
                price_dec = Decimal(price_raw)
            except (InvalidOperation, ValueError):
                price_dec = Decimal(0)
    
            data = {
                "brand": str(getattr(r.lens.brand, "name", "")) or "",
                "range_id": r.id,
                "lens_model": getattr(r.lens, "model_name", str(r.lens)),
                "title": str(getattr(r.lens, "title", "")) or "",
                "design": str(getattr(r.lens, "design", "")) or "",
                "availability": str(getattr(r.lens, "availability", "")) or "",
                "plus_sphere_group": f"{float(r.plus_sphere_group):,}" if r.plus_sphere_group is not None else "N/A",
                "minus_sphere_group": f"{float(r.minus_sphere_group):,}" if r.minus_sphere_group is not None else "N/A",
                "plus_cylinder_group": f"{float(r.plus_cylinder_group):,}" if r.plus_cylinder_group is not None else "N/A",
                "minus_cylinder_group": f"{float(r.minus_cylinder_group):,}" if r.minus_cylinder_group is not None else "N/A",
                "ri": str(getattr(r.lens, "refractive_index", "")) or "",
                "price":f"{int(price_dec):,}" if price_dec else "0",
                "unique_slens_id": str(getattr(r, "unique_slens_id", "")) or "",
                "notes": getattr(r, "notes", "") or "",
                }
                
           
            
            # Conditional fields based on occupational lens
            if getattr(r.lens, "occupational_lens", True):
                data["occupational_lens"] = True
                data["best_occupational_use"] = getattr(r.lens, "best_occupational_use", "") or ""
            else:
                data["occupational_lens"] = False
                data["best_occupational_use"] = "This lens is not intended for a particular occupation."
            if getattr(r.lens, "photochromic", True):
                data["photochromic"] = True
                data["transition"]=True if getattr(r.lens, "transition", True) else False
                data["rayblock_precentage"] = getattr(r.lens, "rayblock_precentage", "") or ""
                
            else:
                data["photochromic"] = False
                data["rayblock_precentage"] = ""
                
            if getattr(r.lens, "antireflex", True):
                data["antireflex"] = True
                data["antireflexcolor"] = getattr(r.lens, "antireflexcolor", "") or ""
                data["antireflexfeature"] = getattr(r.lens, "antireflexfeature", "") or ""
            else:
                data["antireflex"] = False
                data["antireflexcolor"] =""
                data["antireflexfeature"] =""
                     
            if getattr(r.lens, "polarized", True):
                data["polarized"] = True
                
            else:
                data["polarized"] = False
         
     
            
            # Append to results
            results.append(data)
        
        
            
        return results
    

        



    od_match = nearest_for_eye(od_sph, od_cyl)
    os_match = nearest_for_eye(os_sph, os_cyl)
    print(os_match)
    if not od_match and not os_match:
        return JsonResponse({"status": "no_match"})

    return JsonResponse({
        "status": "ok",
        "od_matches": od_match,
        "os_matches": os_match
    }) 



@csrf_exempt
def submit_lens(request):

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"})

        patient_id = data.get("patient_id")
        refraction_id = data.get("refraction_id")
        unique_slens_id = data.get("unique_slens_id")
        eye = data.get("eye")
        selected_slens_title = data.get("selected_slens_title")

        # Required fields check
        if not patient_id or not refraction_id or not unique_slens_id or not eye or not selected_slens_title:
            return JsonResponse({"success": False, "error": "Missing required fields"})

        # Validate Refraction exists
        try:
            Refraction.objects.get(refraction_id=refraction_id)
        except Refraction.DoesNotExist:
            return JsonResponse({"success": False, "error": "Refraction not found"})

        # Prevent duplicate title for this refraction
        if SelectedSpectacleLens.objects.filter(refraction_id=refraction_id, title=selected_slens_title,eye=eye).exists():
            return JsonResponse({
                "success": False,
                "error": "This title was selected previously for this refraction."
            })

        # Create record
        SelectedSpectacleLens.objects.create(
            title=selected_slens_title,
            patient_id=patient_id,
            refraction_id=refraction_id,
            unique_slens_id=unique_slens_id,
            eye=eye,
        )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})

def load_selected_lenses(request, patient_id):
    selected_lenses = SelectedSpectacleLens.objects.filter(patient_id=patient_id)
    result = []

    for sel in selected_lenses:
        # Try to get LensPowerRange and linked SpectacleLens
        try:
            optic = LensPowerRange.objects.select_related("lens__brand").get(unique_slens_id=sel.unique_slens_id)
            lens = optic.lens
        except LensPowerRange.DoesNotExist:
            optic = None
            lens = None

        result.append({
            "title": sel.title,
            "eye": sel.eye,
            "unique_slens_id": sel.unique_slens_id,
            "refraction_id": sel.refraction_id,

            # From optic database
            "brand": lens.brand.name if lens else None,
            "lens_model": lens.model_name if lens else None,
            "ri": str(lens.refractive_index) if lens else None,
     
            "occupational_lens": bool(lens.occupational_lens) if lens else False,
            "antireflex": bool(lens.antireflex) if lens else False,
            "polarized": bool(lens.polarized) if lens else False,
            "photochromic": bool(lens.photochromic) if lens else False,

            # From LensPowerRange
            "price": optic.price if optic else None,
        })
        print(lens.antireflex)

    return JsonResponse({"lenses": result})
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def delete_lens(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            unique_slens_id = data.get("unique_slens_id")
            patient_id = data.get("patient_id")
            eye=data.get("eye")
            title=data.get("title")
            SelectedSpectacleLens.objects.filter(
            unique_slens_id=unique_slens_id, 
            patient_id=patient_id,
            eye=eye,
            title=title
            
            
            ).delete()
            return JsonResponse({"success": True})
        except SelectedSpectacleLens.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lens not found"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})
