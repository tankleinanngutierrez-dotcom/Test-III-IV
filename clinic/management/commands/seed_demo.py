from django.core.management.base import BaseCommand
from clinic.models import Specialty, Doctor
class Command(BaseCommand):
    help="Load demonstration specialties and doctors."
    def handle(self,*args,**options):
        data=[
          ("Family Medicine","Dr. Alex Santos","General checkups and preventive care for all ages.",500,True),
          ("Cardiology","Dr. Maria Reyes","Heart health, blood pressure, and cardiovascular care.",900,True),
          ("Dermatology","Dr. Daniel Lim","Skin, hair, and nail health consultations.",750,True),
          ("Pediatrics","Dr. Sofia Cruz","Compassionate care for infants, children, and teens.",650,True),
          ("Neurology","Dr. Miguel Garcia","Evaluation of headaches and nervous system conditions.",1000,False),
          ("Orthopedics","Dr. Nina Flores","Bone, joint, and mobility care.",850,True),
          ("Family Medicine","Dr. Paolo Mendoza","Wellness visits and chronic condition support.",550,True),
        ]
        for spec,name,bio,fee,accepting in data:
            specialty,_=Specialty.objects.get_or_create(name=spec)
            Doctor.objects.get_or_create(full_name=name,defaults={"specialty":specialty,"bio":bio,"consultation_fee":fee,"is_accepting":accepting})
        self.stdout.write(self.style.SUCCESS("Demo specialties and doctors are ready."))
