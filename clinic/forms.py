import re
from django import forms
from django.utils import timezone
from .models import Doctor, Appointment

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["full_name","specialty","bio","consultation_fee","photo","is_accepting"]
        labels = {"full_name":"Doctor's full name","consultation_fee":"Consultation fee (₱)","is_accepting":"Accepting new patients"}
        help_texts = {"full_name":"Enter the doctor's first and last name.","consultation_fee":"Must be greater than ₱0.00.","photo":"Optional profile photo."}
        widgets = {
            "full_name":forms.TextInput(attrs={"class":"field","placeholder":"Dr. Alex Santos"}),
            "specialty":forms.Select(attrs={"class":"field"}),
            "bio":forms.Textarea(attrs={"class":"field","rows":4}),
            "consultation_fee":forms.NumberInput(attrs={"class":"field","min":"0.01","step":"0.01"}),
            "photo":forms.ClearableFileInput(attrs={"class":"field","accept":"image/*"}),
            "is_accepting":forms.CheckboxInput(attrs={"class":"check-field"}),
        }
    def clean_consultation_fee(self):
        fee = self.cleaned_data["consultation_fee"]
        if fee <= 0: raise forms.ValidationError("Consultation fee must be greater than 0.")
        return fee

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient_name","email","phone","appointment_date","time_slot","visit_type","reason"]
        labels = {"patient_name":"Patient name","appointment_date":"Appointment date","time_slot":"Available time","visit_type":"Visit type","reason":"Reason for visit"}
        help_texts = {"phone":"Use 09XXXXXXXXX or +639XXXXXXXXX.","reason":"Please enter at least 10 characters."}
        widgets = {
            "patient_name":forms.TextInput(attrs={"class":"field","autocomplete":"name"}),
            "email":forms.EmailInput(attrs={"class":"field","autocomplete":"email"}),
            "phone":forms.TextInput(attrs={"class":"field","placeholder":"09123456789"}),
            "appointment_date":forms.DateInput(attrs={"class":"field","type":"date"}),
            "time_slot":forms.Select(attrs={"class":"field"}),
            "visit_type":forms.Select(attrs={"class":"field"}),
            "reason":forms.Textarea(attrs={"class":"field","rows":4,"maxlength":300}),
        }
    def __init__(self, *args, doctor=None, **kwargs):
        self.doctor = doctor
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields["time_slot"].queryset = None
            booked = Appointment.objects.filter(doctor=doctor).exclude(status="Cancelled")
            date = self.data.get("appointment_date") or self.initial.get("appointment_date")
            if date:
                booked = booked.filter(appointment_date=date)
                blocked = set(booked.values_list("time_slot", flat=True))
                self.fields["time_slot"].choices = [("", "Choose a time")] + [(s,s) for s,_ in Appointment.TIME_SLOTS if s not in blocked]
            else:
                self.fields["time_slot"].choices = [("", "Choose a date first")] + Appointment.TIME_SLOTS
    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not (re.fullmatch(r"09\d{9}", phone) or re.fullmatch(r"\+639\d{9}", phone)):
            raise forms.ValidationError("Enter 09XXXXXXXXX or +639XXXXXXXXX.")
        return phone
    def clean_appointment_date(self):
        date = self.cleaned_data["appointment_date"]
        if date < timezone.localdate(): raise forms.ValidationError("Appointment date cannot be in the past.")
        if date.weekday() == 6: raise forms.ValidationError("The clinic is closed on Sundays.")
        return date
    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()
        if len(reason) < 10: raise forms.ValidationError("Reason must contain at least 10 characters.")
        return reason
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("visit_type") == "Teleconsultation" and not cleaned.get("email"):
            self.add_error("email", "Email is required for teleconsultation.")
        if self.doctor and not self.doctor.is_accepting:
            raise forms.ValidationError("This doctor is not accepting appointments.")
        if self.doctor and cleaned.get("appointment_date") and cleaned.get("time_slot"):
            conflict = Appointment.objects.filter(doctor=self.doctor, appointment_date=cleaned["appointment_date"], time_slot=cleaned["time_slot"]).exclude(status="Cancelled")
            if self.instance.pk: conflict = conflict.exclude(pk=self.instance.pk)
            if conflict.exists(): self.add_error("time_slot","This time slot has already been booked.")
        return cleaned
