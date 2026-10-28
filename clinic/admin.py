from django.contrib import admin
from .models import Specialty, Doctor, Appointment
admin.site.register(Specialty)
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display=("full_name","specialty","consultation_fee","is_accepting")
    list_filter=("specialty","is_accepting")
    search_fields=("full_name","bio")
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display=("id","patient_name","doctor","appointment_date","time_slot","status")
    list_filter=("status","visit_type","appointment_date")
