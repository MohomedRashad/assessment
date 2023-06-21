from datetime import datetime
from rest_framework.exceptions import ValidationError
from apps.GPService.models import Order, PharmacyNotification

def check_meeting_slot_time(starting_time, ending_time):
    start_time = datetime.strptime(starting_time.isoformat(), "%H:%M:%S")
    end_time = datetime.strptime(ending_time.isoformat(), "%H:%M:%S")
    delta = end_time - start_time
    seconds = delta.total_seconds()
    minutes = seconds / 60
    if minutes == 15:
        return True
    else:
        return False

def create_order(type, total_amount, **kwargs):
    #The order will be determined by the "type" argument.
    #available order types: FORM_ASSESSMENT, and VIDEO_ASSESSMENT
    if type == 'FORM_ASSESSMENT':
        if 'form_assessment' in kwargs:
            #Creating the FORM_ASSESSMENT order
            order = Order(type = type, form_assessment = kwargs.get('form_assessment'), total_amount = total_amount)
            order.save()
    elif type == 'VIDEO_ASSESSMENT':
        if 'appointment' in kwargs:
            #Creating the VIDEO_ASSESSMENT order
            order = Order(type = type, appointment = kwargs.get('appointment'), total_amount = total_amount)
            order.save()
    else:
        raise ValidationError("Invalid order type!")

def obtain_the_selected_pharmacy_of_the_patient(prescription):
    #returns a pharmacy object
    # getting the pharmacy which was pre-selected by the patient in the beginning
    # The patient object will be obtained by the prescription instance passed to this function as a parameter
    # A logic check to identify whether an appointment or a form assessment is in the prescription
    if prescription.appointment is not None:
        return prescription.appointment.patient.pharmacy
    elif prescription.form_assessment is not None:
        return prescription.form_assessment.patient.pharmacy
    else:
        raise ValidationError("An error has occurred")

def send_prescription_notification_to_pharmacy(pharmacy, prescription):
    pharmacy_notification = PharmacyNotification(pharmacy=pharmacy, prescription=prescription)
    pharmacy_notification.save()
    print("Notification for the pharmacy has been sent")


