from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Doctor, Specialty, Appointment
from .forms import DoctorForm, AppointmentForm

def is_htmx(request): return request.headers.get("HX-Request") == "true"

def doctor_list(request):
    doctors = Doctor.objects.select_related("specialty").all()
    query = request.GET.get("q","").strip()
    specialty = request.GET.get("specialty","")
    sort = request.GET.get("sort","name")
    if query: doctors = doctors.filter(full_name__icontains=query) | doctors.filter(bio__icontains=query)
    if specialty: doctors = doctors.filter(specialty__slug=specialty)
    order = {"fee-low":"consultation_fee","fee-high":"-consultation_fee","name":"full_name"}.get(sort,"full_name")
    doctors = doctors.order_by(order)
    paginator = Paginator(doctors, 6)
    page = paginator.get_page(request.GET.get("page"))
    context={"page_obj":page,"doctors":page.object_list,"specialties":Specialty.objects.all(),"query":query,"selected_specialty":specialty,"sort":sort,"result_count":paginator.count}
    template = "clinic/partials/_doctor_grid.html" if is_htmx(request) else "clinic/doctor_list.html"
    return render(request,template,context)

def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related("specialty"),pk=pk)
    return render(request,"clinic/doctor_detail.html",{"doctor":doctor})

def available_slots(request, pk):
    doctor=get_object_or_404(Doctor,pk=pk)
    date=request.GET.get("appointment_date")
    booked=Appointment.objects.filter(doctor=doctor,appointment_date=date).exclude(status="Cancelled").values_list("time_slot",flat=True) if date else []
    return render(request,"clinic/partials/_slot_options.html",{"slots":Appointment.TIME_SLOTS,"booked":set(booked)})

def book_appointment(request, pk):
    doctor=get_object_or_404(Doctor,pk=pk)
    if not doctor.is_accepting: raise Http404("This doctor is not accepting appointments.")
    if request.method=="POST":
        form=AppointmentForm(request.POST,doctor=doctor)
        if form.is_valid():
            appt=form.save(commit=False); appt.doctor=doctor
            try:
                appt.save()
            except IntegrityError:
                form.add_error("time_slot","This time slot has just been booked. Please choose another.")
            else:
                if is_htmx(request):
                    response=HttpResponse("")
                    response["HX-Redirect"]=f"/appointments/{appt.pk}/confirmation/"
                    response["HX-Trigger"]='{"toast":{"type":"success","message":"Appointment booked successfully."}}'
                    return response
                return redirect("appointment_confirmation",pk=appt.pk)
        if is_htmx(request):
            return render(request,"clinic/partials/_appointment_form_fields.html",{"form":form,"doctor":doctor},status=422)
    else: form=AppointmentForm(doctor=doctor)
    return render(request,"clinic/appointment_form.html",{"form":form,"doctor":doctor})

def appointment_confirmation(request,pk):
    appointment=get_object_or_404(Appointment.objects.select_related("doctor","doctor__specialty"),pk=pk)
    return render(request,"clinic/appointment_success.html",{"appointment":appointment})

def manage_doctors(request):
    doctors=Doctor.objects.select_related("specialty").all()
    q=request.GET.get("q","")
    if q: doctors=doctors.filter(full_name__icontains=q)
    return render(request,"clinic/doctor_manage.html",{"doctors":doctors,"q":q})

def doctor_create(request):
    form=DoctorForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid():
        form.save(); messages.success(request,"Doctor added successfully."); return redirect("manage_doctors")
    return render(request,"clinic/doctor_form.html",{"form":form,"heading":"Add doctor"})

def doctor_edit(request,pk):
    doctor=get_object_or_404(Doctor,pk=pk)
    form=DoctorForm(request.POST or None,request.FILES or None,instance=doctor)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Doctor updated."); return redirect("manage_doctors")
    return render(request,"clinic/doctor_form.html",{"form":form,"heading":"Edit doctor"})

@require_POST
def doctor_toggle(request,pk):
    doctor=get_object_or_404(Doctor,pk=pk); doctor.is_accepting=not doctor.is_accepting; doctor.save()
    if is_htmx(request): return render(request,"clinic/partials/_doctor_row.html",{"doctor":doctor})
    return redirect("manage_doctors")

@require_POST
def doctor_delete(request,pk):
    doctor=get_object_or_404(Doctor,pk=pk)
    if doctor.appointments.exists():
        messages.error(request,"Doctor has appointments and cannot be deleted.")
    else: doctor.delete(); messages.success(request,"Doctor deleted.")
    return redirect("manage_doctors")

def manage_appointments(request):
    appointments=Appointment.objects.select_related("doctor").all()
    status=request.GET.get("status","All")
    if status!="All": appointments=appointments.filter(status=status)
    return render(request,"clinic/appointment_manage.html",{"appointments":appointments,"active_status":status})

@require_POST
def appointment_status(request,pk,status):
    if status not in ("Confirmed","Cancelled"): raise Http404()
    appt=get_object_or_404(Appointment,pk=pk); appt.status=status; appt.save()
    if is_htmx(request): return render(request,"clinic/partials/_appointment_row.html",{"appointment":appt})
    return redirect("manage_appointments")

def custom_404(request,exception): return render(request,"404.html",status=404)
