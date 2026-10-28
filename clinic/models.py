from django.db import models
from django.utils.text import slugify
class Specialty(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name

class Doctor(models.Model):
    full_name = models.CharField(max_length=120)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="doctors")
    bio = models.TextField()
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.ImageField(upload_to="doctors/", blank=True)
    is_accepting = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["full_name"]
    def __str__(self): return self.full_name

class Appointment(models.Model):
    VISIT_CHOICES = [("In-Clinic","In-Clinic"),("Teleconsultation","Teleconsultation")]
    STATUS_CHOICES = [("Pending","Pending"),("Confirmed","Confirmed"),("Cancelled","Cancelled")]
    TIME_SLOTS = [(x,x) for x in ["09:00","10:00","11:00","13:00","14:00","15:00"]]
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    patient_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=13)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    visit_type = models.CharField(max_length=20, choices=VISIT_CHOICES, default="In-Clinic")
    reason = models.CharField(max_length=300)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-appointment_date","time_slot"]
        constraints = [models.UniqueConstraint(fields=["doctor","appointment_date","time_slot"], name="unique_doctor_appointment_slot")]
    @property
    def reference_number(self): return f"MB-{self.pk:06d}"
    def __str__(self): return f"{self.reference_number} — {self.patient_name}"
