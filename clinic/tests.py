from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Specialty, Doctor, Appointment
from .forms import AppointmentForm, DoctorForm

class MediBookTests(TestCase):
    def setUp(self):
        self.specialty=Specialty.objects.create(name="Family Medicine")
        self.doctor=Doctor.objects.create(full_name="Dr. Alex Santos",specialty=self.specialty,bio="Family medicine and preventive care.",consultation_fee=500,is_accepting=True)
        self.date=timezone.localdate()+timedelta(days=1)
        while self.date.weekday()==6: self.date+=timedelta(days=1)
        self.client=Client()
    def valid_data(self,**overrides):
        data={"patient_name":"Jamie Cruz","email":"jamie@example.com","phone":"09123456789","appointment_date":self.date.isoformat(),"time_slot":"09:00","visit_type":"In-Clinic","reason":"Recurring headache"}
        data.update(overrides); return data
    def test_home_page(self):
        response=self.client.get(reverse("doctor_list")); self.assertEqual(response.status_code,200); self.assertContains(response,"Dr. Alex Santos")
    def test_phone_validation(self):
        form=AppointmentForm(self.valid_data(phone="123"),doctor=self.doctor); self.assertFalse(form.is_valid()); self.assertIn("phone",form.errors)
    def test_teleconsult_email_required(self):
        form=AppointmentForm(self.valid_data(email="",visit_type="Teleconsultation"),doctor=self.doctor); self.assertFalse(form.is_valid()); self.assertIn("email",form.errors)
    def test_reason_minimum(self):
        form=AppointmentForm(self.valid_data(reason="short"),doctor=self.doctor); self.assertFalse(form.is_valid())
    def test_fee_must_be_positive(self):
        form=DoctorForm({"full_name":"Dr Test","specialty":self.specialty.pk,"bio":"Bio","consultation_fee":"0","is_accepting":"on"}); self.assertFalse(form.is_valid())
    def test_booking_saves(self):
        response=self.client.post(reverse("book_appointment",args=[self.doctor.pk]),self.valid_data())
        self.assertEqual(response.status_code,302); self.assertEqual(Appointment.objects.count(),1)
    def test_double_booking_rejected(self):
        Appointment.objects.create(doctor=self.doctor,patient_name="A Person",email="a@b.com",phone="09123456789",appointment_date=self.date,time_slot="09:00",visit_type="In-Clinic",reason="Long enough reason")
        form=AppointmentForm(self.valid_data(),doctor=self.doctor); self.assertFalse(form.is_valid())
    def test_non_accepting_doctor_blocked(self):
        self.doctor.is_accepting=False; self.doctor.save()
        response=self.client.get(reverse("book_appointment",args=[self.doctor.pk])); self.assertEqual(response.status_code,404)
    def test_htmx_directory_partial(self):
        response=self.client.get(reverse("doctor_list"),HTTP_HX_REQUEST="true"); self.assertEqual(response.status_code,200); self.assertTemplateUsed(response,"clinic/partials/_doctor_grid.html")
