from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from django.conf import settings
from rest_framework.views import APIView
from django.http import Http404
from django.db.models import Q
from rest_framework import status
from apps.users.permissions import DoctorWriteOnly, IsAllowedToAccessAssessment, SystemAdminOrReadOnly, PharmacyOrReadOnly, PatientWriteOnly
from apps.users.models import Pharmacy, Roles
from .models import AppointmentStatus, FormAssessmentType, OrderType, PharmacyNotification, PharmacyReviewStatus, Availability, Appointment, Medicine, Treatment, FormAssessmentQuestion, FormAssessment, FormAssessmentAnswer, FormAssessmentFeedback, Prescription, Order, Country, RecommendedVaccine
from .serializers import AvailabilitySerializer, AppointmentSerializer, AddAppointmentSerializer, PharmacyNotificationSerializer, UpdateAppointmentStatusSerializer, MedicineSerializer, CountrySerializer, ViewRecommendedVaccineSerializer, AddRecommendedVaccineSerializer, TreatmentSerializer, FormAssessmentQuestionSerializer, ViewAllFormAssessmentSerializer, ViewFormAssessmentSerializer, ViewFormAssessmentAnswerSerializer, AddFormAssessmentAnswerSerializer, ViewFormAssessmentFeedbackSerializer, AddFormAssessmentFeedbackSerializer, PrescriptionSerializer, OrderSerializer, PharmacySerializer
from datetime import datetime
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .services import check_meeting_slot_time, create_order, obtain_the_selected_pharmacy_of_the_patient, send_prescription_notification_to_pharmacy
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import path

class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [DoctorWriteOnly]

    def get_queryset(self):
        if self.request.user.role == Roles.SUPER_ADMIN:
            return Availability.objects.all()
        elif self.request.user.role == Roles.DOCTOR:
            return Availability.objects.filter(doctor=self.request.user.doctor)
        elif self.request.user.role == Roles.PATIENT:
            return Availability.objects.filter(date__gte = timezone.now().date(), is_booked = False)

    @action(methods=['get'], detail=False, url_path='(?P<doctor_id>[^/.]+)/availabilities')
    def get_all_availabilities_for_a_given_doctor(self, request, doctor_id):
        queryset = Availability.objects.filter(doctor__id=doctor_id, date__gte = timezone.now().date(), is_booked=False)
        serializer = AvailabilitySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if Availability.objects.filter(
            date=self.request.data.get('date'),
            starting_time=self.request.data.get('starting_time'),
            ending_time=self.request.data.get('ending_time'),
            doctor=self.request.user.doctor).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        else:
            serializer.save(doctor=self.request.user.doctor)

    def perform_update(self, serializer):
        availability = self.get_object()
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if availability.is_booked:
            raise ValidationError("This availability instance cannot be modified as it has already been booked before")            
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        elif availability.starting_time != datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S').time() and availability.starting_time != datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S').time():
            if Availability.objects.filter(
                date=self.request.data['date'],
                starting_time = self.request.data['starting_time'],
                ending_time=self.request.data['ending_time'],
                doctor=self.request.user.doctor).exists():
                raise ValidationError("This availability instance has already been added before")
        else:
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        availability = self.get_object()
        if availability.doctor != self.request.user.doctor:
            raise ValidationError("You are not authorized to delete this availability instance")
        elif availability.is_booked:
            raise ValidationError("This availability instance cannot be deleted as it has been associated with an appointment")
        else:
            super().perform_destroy(instance)

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [PatientWriteOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'destroy':
            return UpdateAppointmentStatusSerializer
        elif self.action == 'create':
            return AddAppointmentSerializer
        return super(AppointmentViewSet, self).get_serializer_class()

    def get_queryset(self):
        if self.request.user.role == Roles.DOCTOR:
            return Appointment.objects.filter(availability__doctor_id=self.request.user.doctor)
        elif self.request.user.role == Roles.PATIENT:
            return Appointment.objects.filter(patient=self.request.user.patient)

    @transaction.atomic
    def perform_create(self, serializer):
        availability = get_object_or_404(
            Availability, id = self.request.data.get('availability'))
        if Appointment.objects.filter(
            patient=self.request.user.patient,
            availability=self.request.data.get('availability')).exclude(
            status='CANCELED').exists():
            raise ValidationError("This appointment has already been added before")
        else:
            #Adding the appointment
            serializer.save(patient=self.request.user.patient)
            #Updating the chosen availability status to booked.
            availability.is_booked = True
            availability.save()

    @transaction.atomic
    def perform_update(self, serializer):
        appointment = self.get_object()
        availability = get_object_or_404(Availability, id = appointment.availability.id)
        if not 'status' in self.request.data:
            raise ValidationError("The status has not been provided")
        elif appointment.status == AppointmentStatus.COMPLETED:
            raise ValidationError("This appointment cannot be modified as it has already been completed")
        elif self.request.data['status'] == AppointmentStatus.CANCELED:
            #An appointment can be deleted only if the current status is set to 'BOOKED'
            if appointment.status == AppointmentStatus.ONGOING:
                raise ValidationError("This appointment cannot be deleted, as it is ongoing at the moment")
            else:
                    #Updating the availability status to not booked.
                    availability.is_booked = False
                    availability.save()
                        #Setting the appointment status to 'CANCELED'
                    super().perform_update(serializer)
        else:
            #a condition to check whether the appointment status is ONGOING or COMPLETED
            if self.request.data['status'] == AppointmentStatus.ONGOING:
                #Setting the appointment status to ONGOING
                super().perform_update(serializer)
            elif self.request.data['status'] == AppointmentStatus.COMPLETED:
                #Since the appointment status is completed, an order should be created for the appointment instance
                #Creating the order for the completed appointment
                order = {'appointment': appointment}
                create_order(OrderType.VIDEO_ASSESSMENT, availability.doctor_charge, **order)
                #Setting the appointment status to COMPLETED.
                super().perform_update(serializer)

class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        if self.request.user.role == Roles.SUPER_ADMIN:
            return Prescription.objects.all()
        elif self.request.user.role == Roles.DOCTOR:
            return Prescription.objects.filter(Q(appointment__availability__doctor=self.request.user.doctor) | Q(form_assessment__doctor=self.request.user.doctor))
        elif self.request.user.role == Roles.PATIENT:
            return Prescription.objects.filter(Q(appointment__patient=self.request.user.patient) | Q(form_assessment__patient=self.request.user.patient))
        elif self.request.user.role == Roles.PHARMACY:
            return Prescription.objects.filter(pharmacy = self.request.user)

    def perform_create(self, serializer):
        #todo: should implement validation checks to ensure only the doctor user type can add prescriptions
        # Validate and get the medicine instances into a new dictionary before continuing
        medicines = []
        for medicine_id in self.request.data.pop('medicine', []):
            medicine = get_object_or_404(Medicine, id=medicine_id)
            medicines.append(medicine)
        prescription = serializer.save()
        # Add the related medicines to the prescription in bulk using set method
        prescription.medicines.add(*medicines)

    @transaction.atomic
    def perform_update(self, instance):
        #todo: should implement proper permission and user type validations to allow specific data to be updated in the prescription instance
        validated_data = instance.validated_data
        # Check if the pharmacy_review_status is rejected and reason_for_rejection is not provided
        if 'pharmacy_review_status' in validated_data and validated_data['pharmacy_review_status'] == 'REJECTED' and 'reason_for_rejection' not in validated_data:
            raise ValidationError('Reason for rejection is required when pharmacy review status is set to rejected.')
        elif 'is_accepted' in validated_data and validated_data['is_accepted'] == True:
            #todo: should implement a logic to update the is_accepted field only once.
            #todo: only the patient user type can update the is_accepted property of a prescription
            prescription = instance.save()
            #If the patient accepted the prescription, the related pharmacy should get a notification
            #The pharmacy will be pree-selected by the patient in the beginning
            pharmacy = obtain_the_selected_pharmacy_of_the_patient(prescription)
            #Making sure the returned pharmacy object is a valid one before sending the notification
            if pharmacy is not None:
                send_prescription_notification_to_pharmacy(pharmacy, prescription)
            else:
                raise ValidationError("Unable to obtain the pharmacy which was pree-selected by the patient")
        else:
            if 'pharmacy_review_status' in validated_data:
                #todo: should implement a logic to update the read status of the pharmacy notification for the current prescription.
                super().perform_update(instance)
            else:
                super().perform_update(instance)

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [SystemAdminOrReadOnly]

class RecommendedVaccineViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'destroy':
            return AddRecommendedVaccineSerializer
        elif self.request.query_params.get('country'):
            return ViewRecommendedVaccineSerializer
        return super(RecommendedVaccineViewSet, self).get_serializer_class()

    def get_queryset(self):
        country = self.request.query_params.get('country')
        if country is not None:
            return RecommendedVaccine.objects.filter(country__name__startswith=country)
        return self.queryset

class FormAssessmentQuestionViewSet(viewsets.ViewSet):
    def list(self, request):
        treatment = self.request.query_params.get('treatment')
        queryset = FormAssessmentQuestion.objects.all()
        if treatment is not None:
            queryset = queryset.filter(treatments__name=treatment)
        serializer = FormAssessmentQuestionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FormAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes = [PatientWriteOnly, IsAllowedToAccessAssessment]
    serializer_class = ViewAllFormAssessmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']

    def get_queryset(self):
        if self.request.user.role == Roles.DOCTOR:
            return FormAssessment.objects.filter(Q(doctor=self.request.user.doctor) | Q(doctor__isnull=True))
        elif self.request.user.role == Roles.PATIENT:
            return FormAssessment.objects.filter(patient=self.request.user.patient)
        elif self.request.user.role == Roles.SUPER_ADMIN:
            return FormAssessment.objects.all()

    @transaction.atomic
    @action(methods=['post'], detail=False, url_path='form-assessment-answers', permission_classes=[PatientWriteOnly])
    def create_form_assessment(self, request):
        answer_data = [] #a dictionary of answers which will be added to the database at once.
        if not 'type' in self.request.data:
            raise ValidationError("The form assessment type is required.")
        elif not 'answers' in self.request.data:
            raise ValidationError("The answers are required")
        else:
            #creating a form assessment instance
            form_assessment = FormAssessment(
                patient = self.request.user.patient,
                type = self.request.data.get('type'))
            form_assessment.save()
            #Adding the answers to the database.
            for current_answer in request.data['answers']:
                answer = {
                    'form_assessment_question': current_answer['question'],
                    'form_assessment': form_assessment.id,
                    'answer': current_answer['answer']
                    }
                answer_data.append(answer)
            serializer = AddFormAssessmentAnswerSerializer(data = answer_data, many=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            queryset = FormAssessment(pk = form_assessment.id)
            return_serializer = ViewFormAssessmentSerializer(queryset)
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
            
    @action(methods=['put'], detail=False, url_path='(?P<form_assessment_id>\d+)/form-assessment-answers', permission_classes=[PatientWriteOnly])
    def update_form_assessment_answers(self, request, form_assessment_id):
        updated_answers = [] #a dictionary of answers which will be updated at once.
        if not 'answers' in self.request.data:
            raise ValidationError("The answers are required")
        else:
            #getting the form assessment instance
            form_assessment = get_object_or_404(FormAssessment, id = form_assessment_id)
            #the answers of a form assessment can be updated only if the form assessment has not been assessed at the moment
            if form_assessment.is_assessed:
                raise ValidationError("The answers cannot be updated, as the form assessment has already been assessed by a doctor")
            else:
                #Updating the answers.
                for current_answer in request.data['answers']:
                    form_assessment_answer = get_object_or_404(FormAssessmentAnswer, id = current_answer['answer_id'], form_assessment = form_assessment.id)
                    form_assessment_answer.answer = current_answer['answer']
                    form_assessment_answer.save()
                    updated_answers.append(form_assessment_answer) # Add the updated form assessment answer to the list of updated answers
                    serializer = ViewFormAssessmentAnswerSerializer(updated_answers, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


    @transaction.atomic
    @action(methods=['get', 'post'], detail=False, url_path='(?P<form_assessment_id>\d+)/form-assessment-feedbacks', permission_classes=[DoctorWriteOnly])
    def form_assessment_feedback(self, request, form_assessment_id):
        if request.method == 'GET':
            form_assessment = get_object_or_404(FormAssessment, id = form_assessment_id)
            queryset = FormAssessmentFeedback.objects.filter(form_assessment = form_assessment_id)
            if self.request.user.role == Roles.DOCTOR:
                if form_assessment.doctor is not None and form_assessment.doctor != self.request.user.doctor:
                    raise PermissionDenied
            elif self.request.user.role == Roles.PATIENT:
                if form_assessment.patient != self.request.user.patient:
                    raise PermissionDenied
            serializer = ViewFormAssessmentFeedbackSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'POST':
            #assumption: only the doctor user type can invoke the modification of a form assessment
            form_assessment = get_object_or_404(FormAssessment, pk = form_assessment_id)
            if form_assessment.is_assessed and form_assessment.doctor != self.request.user.doctor:
                raise ValidationError("This form assessment has already been assessed by another doctor")
            else:
                    #updating the form assessment instance with the doctor details
                    form_assessment.doctor = self.request.user.doctor
                    form_assessment.is_assessed = True
                    form_assessment.assessed_date = datetime.today()
                    form_assessment.save()
                    #creating a dictionary to hold the form assessment feedback data.
                    form_assessment_feedback_data = {
                        'form_assessment': form_assessment.id,
                        'provided_feedback': self.request.data.get('provided_feedback')
                    }
                    #adding the feedback to the database using the serializer
                    serializer = AddFormAssessmentFeedbackSerializer(data = form_assessment_feedback_data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                    #Creating the order for assessed form assessment
                    order = {'form_assessment': form_assessment}
                    create_order(OrderType.FORM_ASSESSMENT, settings.FORM_ASSESSMENT_AMOUNT, **order)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['put'], detail=False, url_path='(?P<form_assessment_id>\d+)/form-assessment-feedbacks/(?P<form_assessment_feedback_id>\d+)', permission_classes=[DoctorWriteOnly])
    def update_form_assessment_feedback(self, request, form_assessment_id, form_assessment_feedback_id):
        form_assessment = get_object_or_404(FormAssessment, pk = form_assessment_id)
        if not 'provided_feedback' in self.request.data:
            raise ValidationError("The provided_feedback is required.")
        elif form_assessment.doctor != self.request.user.doctor:
            raise  ValidationError("You are not authorized to update the form assessment feedback")
        else:
            #updating the feedback
            form_assessment_feedback = get_object_or_404(FormAssessmentFeedback, pk = form_assessment_feedback_id, form_assessment = form_assessment.id)
            form_assessment_feedback.provided_feedback = self.request.data.get('provided_feedback')
            form_assessment_feedback.save()
            serializer = ViewFormAssessmentFeedbackSerializer(form_assessment_feedback)
            return Response(serializer.data, status=status.HTTP_200_OK)

class OrderViewSet(viewsets.ViewSet):
    def list(self, request):
        type = self.request.query_params.get('type')
        queryset = Order.objects.all()
        if self.request.user.role == Roles.DOCTOR:
            queryset = queryset.filter(Q(appointment__availability__doctor=self.request.user.doctor) | Q(form_assessment__doctor=self.request.user.doctor))
        elif self.request.user.role == Roles.PATIENT:
            queryset = queryset.filter(Q(appointment__patient=self.request.user.patient) | Q(form_assessment__patient=self.request.user.patient))
        elif self.request.user.role == Roles.PHARMACY:
            #todo
            print("Should implement the pharmacy logic")
        if type is not None:
            queryset = queryset.filter(type = type)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [PharmacyOrReadOnly]

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Creating new pharmacies is not allowed.")

    @action(methods=['get'], detail=False, url_path='(?P<pharmacy_id>[^/.]+)/notifications')
    def retrieve_notifications_for_a_given_pharmacy(self, request, pharmacy_id):
        #todo: should implement a way to filter the notifications by read status
        queryset = PharmacyNotification.objects.filter(pharmacy__id=pharmacy_id)
        serializer = PharmacyNotificationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
