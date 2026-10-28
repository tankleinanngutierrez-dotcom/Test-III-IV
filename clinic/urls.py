from django.urls import path
from . import views
urlpatterns=[
 path("",views.doctor_list,name="doctor_list"),
 path("doctors/<int:pk>/",views.doctor_detail,name="doctor_detail"),
 path("doctors/<int:pk>/book/",views.book_appointment,name="book_appointment"),
 path("doctors/<int:pk>/slots/",views.available_slots,name="available_slots"),
 path("appointments/<int:pk>/confirmation/",views.appointment_confirmation,name="appointment_confirmation"),
 path("manage/doctors/",views.manage_doctors,name="manage_doctors"),
 path("manage/doctors/add/",views.doctor_create,name="doctor_create"),
 path("manage/doctors/<int:pk>/edit/",views.doctor_edit,name="doctor_edit"),
 path("manage/doctors/<int:pk>/toggle/",views.doctor_toggle,name="doctor_toggle"),
 path("manage/doctors/<int:pk>/delete/",views.doctor_delete,name="doctor_delete"),
 path("manage/appointments/",views.manage_appointments,name="manage_appointments"),
 path("manage/appointments/<int:pk>/<str:status>/",views.appointment_status,name="appointment_status"),
]
