from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import status
from datetime import datetime
from rest_framework.exceptions import ValidationError
from .services import check_meeting_slot_time
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Availability, Appointment, FormAssessmentQuestion, FormAssessment, FormAssessmentAnswer, FormAssessmentFeedback, Medicine
from .serializers import AvailabilitySerializer, AppointmentSerializer, AddAppointmentSerializer, UpdateAppointmentStatusSerializer, FormAssessmentQuestionSerializer, ViewFormAssessmentSerializer, FormAssessmentAnswerSerializer, FormAssessmentFeedbackSerializer, MedicineSerializer

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


    def perform_create(self, serializer):
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if Availability.objects.filter(
            date=self.request.data.get('date'),
            starting_time=self.request.data.get('starting_time'),
            ending_time=self.request.data.get('ending_time'),
            doctor=self.request.user).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        else:
            serializer.save(doctor=self.request.user)


    def perform_update(self, serializer):
        availability = self.get_object()
        starting_time = datetime.strptime(self.request.data.get('starting_time'), '%H:%M:%S')
        ending_time = datetime.strptime(self.request.data.get('ending_time'), '%H:%M:%S')
        if availability.is_booked:
            raise ValidationError("This availability instance cannot be modified as it has already been booked before")            
        elif Availability.objects.filter(
            date=self.request.data['date'],
            starting_time=self.request.data['starting_time'],
            ending_time=self.request.data['ending_time'],
            doctor=self.request.user).exists():
            raise ValidationError("This availability instance has already been added before")
        elif not check_meeting_slot_time(
            starting_time.time(),
            ending_time.time()):
            raise ValidationError("The duration of the availability slot should exactly be 15 minutes")
        else:
            super().perform_update(serializer)


    def perform_destroy(self, instance):
        availability = self.get_object()
        if availability.doctor != self.request.user:
            raise ValidationError("You are not authorized to delete this availability instance")
        elif availability.is_booked:
            raise ValidationError("This availability instance cannot be deleted as it has been associated with an appointment")
        else:
            super().perform_destroy(instance)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'destroy':
            return UpdateAppointmentStatusSerializer
        elif self.action == 'create':
            return AddAppointmentSerializer
        return super(AppointmentViewSet, self).get_serializer_class()

    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status is not None:
            self.queryset.filter(status=status, patient=self.request.user)
        else:
            self.queryset.filter(patient=self.request.user)
        return self.queryset

    @transaction.atomic
    def perform_create(self, serializer):
        availability = get_object_or_404(
            Availability, id = self.request.data.get('availability'))
        if Appointment.objects.filter(
            patient=self.request.user,
            availability=self.request.data.get('availability')).exclude(
            status='CANCELED').exists():
            raise ValidationError("This appointment has already been added before")
        else:
            #Adding the appointment
            serializer.save(patient=self.request.user)
            #Updating the chosen availability status to booked.
            availability.is_booked = True
            availability.save()

    @transaction.atomic
    def perform_update(self, serializer):
        appointment = self.get_object()
        if not 'status' in self.request.data:
            raise ValidationError("The status has not been provided")
        elif appointment.status == 'COMPLETED':
            raise ValidationError("This appointment cannot be modified as it has already been completed")
        elif self.request.data['status'] == 'CANCELED':
            #An appointment can be deleted only if the current status is set to 'BOOKED'
            if appointment.status == 'ONGOING':
                raise ValidationError("This appointment cannot be deleted, as it is ongoing at the moment")
            else:
                    #Updating the availability status to not booked.
                    availability = get_object_or_404(
                        Availability, id = appointment.availability.id)
                    availability.is_booked = False
                    availability.save()
                        #Setting the appointment status to 'CANCELED'
                    super().perform_update(serializer)
        else:
            super().perform_update(serializer)

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

class FormAssessmentQuestionViewSet(viewsets.ViewSet):
    def list(self, request):
        treatment = self.request.query_params.get('treatment')
        queryset = FormAssessmentQuestion.objects.all()
        if treatment is not None:
            queryset = queryset.filter(treatments__name__startswith=treatment)
        serializer = FormAssessmentQuestionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FormAssessmentViewSet(viewsets.ViewSet):
    def list(self, request):
        #Returns a list of form assessments of the current patient
        type = self.request.query_params.get('type')
        queryset = FormAssessment.objects.all()
        if type is not None:
            queryset.filter(type=status, patient=self.request.user)
        else:
            queryset.filter(patient=self.request.user)
        serializer = ViewFormAssessmentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        #Returns the detail view of a form assessment based on the given id
        queryset = FormAssessmentAnswer.objects.filter(form_assessment=pk)
        serializer = FormAssessmentAnswerSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='formassessmentanswers')
    def create_form_assessment(self, request):
        if not 'type' in self.request.data:
            raise ValidationError("The form assessment type is required.")
        elif not 'answers' in self.request.data:
            raise ValidationError("The answers are required")
        else:
            #getting the answers array to a variable
            answers = request.data['answers']
            #validating whether the questions provided in the answers array exists in the database
            for current_answer in answers:
                form_assessment_question = get_object_or_404(FormAssessmentQuestion, id = current_answer['question'])
            #creating a form assessment instance
            form_assessment = FormAssessment(patient=self.request.user, type=self.request.data.get('type'))
            form_assessment.save()
            #Adding the answers to the database.
            for current_answer in answers:
                form_assessment_question = get_object_or_404(FormAssessmentQuestion, id = current_answer['question'])
                FormAssessmentAnswer.objects.create(form_assessment_question = form_assessment_question, form_assessment = form_assessment, answer = current_answer['answer'])
            return Response(status=status.HTTP_201_CREATED)
            
    @action(methods=['put'], detail=False, url_path='(?P<form_assessment_id>\d+)/formassessmentanswers')
    def update_form_assessment_answers(self, request, form_assessment_id):
        if not 'answers' in self.request.data:
            raise ValidationError("The answers are required")
        else:
            #getting the form assessment instance
            form_assessment = get_object_or_404(FormAssessment, id = form_assessment_id)
            #the answers of a form assessment can be updated only if the form assessment has not been assessed at the moment
            if form_assessment.is_assessed:
                raise ValidationError("The answers cannot be updated, as the form assessment has been assessed by a doctor")
            else:
                #getting the answers array to a variable
                answers = request.data['answers']
                #validating whether the answer ids provided in the answers array exists in the database
                for current_answer in answers:
                    form_assessment_answer = get_object_or_404(FormAssessmentAnswer, id = current_answer['answer_id'], form_assessment = form_assessment.id)
                    form_assessment_answer.answer = current_answer['answer']
                    form_assessment_answer.save()
                    serializer = FormAssessmentAnswerSerializer(form_assessment_answer)
                    return Response(serializer.data, status=status.HTTP_200_OK)


    @transaction.atomic
    @action(methods=['get', 'post', 'put'], detail=False, url_path='(?P<form_assessment_id>\d+)/formassessmentfeedback')
    def form_assessment_feedback(self, request, form_assessment_id):
        if request.method == 'GET':
            #Returns the feedback of a given form assessment
            queryset = FormAssessmentFeedback.objects.filter(form_assessment = form_assessment_id)
            serializer = FormAssessmentFeedbackSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            #assumption: only the doctor user type can invoke the modification of a form assessment
            #The patient cannot update the form once created
            #A form assessment will only be updated when a doctor performs an assessment of an existing form.
            form_assessment = get_object_or_404(FormAssessment, id = form_assessment_id)
            if not 'provided_feedback' in self.request.data:
                    raise ValidationError("The provided_feedback is required.")
            else:
                    #updating the form assessment instance with the doctor details
                    form_assessment.doctor = self.request.user
                    form_assessment.is_assessed = True
                    form_assessment.assessed_date = datetime.today()
                    form_assessment.save()
                    #adding the feedback to the database
                    form_assessment_feedback = FormAssessmentFeedback(form_assessment = form_assessment, provided_feedback = self.request.data.get('provided_feedback'))
                    form_assessment_feedback.save()
                    return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'PUT':
            if not 'provided_feedback' in self.request.data:
                    raise ValidationError("The provided_feedback is required.")
            else:
                    #updating the feedback
                    form_assessment_feedback = get_object_or_404(FormAssessmentFeedback, form_assessment = form_assessment_id)
                    form_assessment_feedback.provided_feedback = self.request.data.get('provided_feedback')
                    form_assessment_feedback.save()
                    serializer = FormAssessmentFeedbackSerializer(form_assessment_feedback)
                    return Response(serializer.data, status=status.HTTP_200_OK)
