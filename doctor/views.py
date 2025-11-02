
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib.auth.decorators import permission_required
from doctor.models import BrandsSplenss
from doctor.models import OpticsFeature


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
from .models import ImpMenuParts
from django.shortcuts import render, get_object_or_404
from .models import Patient, GH_HealthCondition,GH_Medication,GH_Allergies,GH_FamilialHistory,GH_GeneticalHistory,GH_LifestyleHistory,GH_OcularHistory,GeneralHealthRecord
from django.contrib.auth.decorators import login_required, user_passes_test
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
            pd=pd
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
    
    familial_histroy= GH_FamilialHistory.objects.all()
    
    genetical_history= GH_GeneticalHistory.objects.all()

    lifestyle_history= GH_LifestyleHistory.objects.all()
    
    ocular_history= GH_OcularHistory.objects.all()
    

    

    # Notes

    context = {

        'health_conditions': health_conditions,

        'medications': medications,
        
        'allergies':allergies,
        
        'familial_histroy':familial_histroy,
        
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
    "systemic": split_and_strip(record.systemic_diseases) if record else [],
    "ocular": split_and_strip(record.ocular_history) if record else [],
    "medications": split_and_strip(record.medications) if record else [],
    "allergies": split_and_strip(record.allergies) if record else [],
    "familial": split_and_strip(record.familial_history) if record else [],
    "genetical": split_and_strip(record.genetical_history) if record else [],
    "lifestyle": split_and_strip(record.lifestyle_history) if record else [],
    }

    context = {
        "patient": patient,
        "record": record,            # single instance or None
        "selected_data": selected_data,  # lists for pre-selecting checkboxes
        "health_conditions": GH_HealthCondition.objects.all(),
        "ocular_history": GH_OcularHistory.objects.all(),
        "medications": GH_Medication.objects.all(),
        "allergies": GH_Allergies.objects.all(),
        "familial_histroy": GH_FamilialHistory.objects.all(),
        "genetical_history": GH_GeneticalHistory.objects.all(),
        "lifestyle_history": GH_LifestyleHistory.objects.all(),
    }

    return context


@login_required
@user_passes_test(is_doctor_admin)


def general_health_record(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == "POST":
        systemic = request.POST.get("systemic_selected", "")
        ocular = request.POST.get("ocular_selected", "")
        medications = request.POST.get("medications_selected", "")
        allergies = request.POST.get("allergies_selected", "")
        familial = request.POST.get("familial_selected", "")
        genetical = request.POST.get("genetical_selected", "")
        lifestyle = request.POST.get("lifestyle_selected", "")

        # Check if a record already exists for this patient
        record, created = GeneralHealthRecord.objects.get_or_create(patient=patient)

        # Update the existing or newly created record
        record.systemic_diseases = systemic
        record.ocular_history = ocular
        record.medications = medications
        record.allergies = allergies
        record.familial_history = familial
        record.genetical_history = genetical
        record.lifestyle_history = lifestyle
        record.save()

        # Redirect back to patient profile
        return redirect("doctor:patient_profile", patient_id=patient.patient_id)

    # If GET request, render profile or form
    return render(request, "doctor/patient_profile.html", {"patient": patient})




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



from django.shortcuts import render
import json
@csrf_exempt  # if you already have csrf token in the form, this is optional
def rx_print(request):
    if request.method == "POST":
        rx_data_json = request.POST.get("rx_data")
        rx_data = json.loads(rx_data_json)
        # Now rx_data contains everything you sent
        return render(request, "doctor/rx_print.html", {"rx": rx_data})