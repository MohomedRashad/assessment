"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.files.views import FileViewSet
from apps.users.views import AuthViewSet, UserViewSet
from apps.GPService.views import AvailabilityViewSet, AppointmentViewSet, InvoiceViewSet, MedicineViewSet, RecommendedVaccineViewSet, FormAssessmentQuestionViewSet, FormAssessmentViewSet, PrescriptionViewSet, OrderViewSet, PharmacyViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='users')
router.register('files', FileViewSet, basename='files')
router.register('availabilities', AvailabilityViewSet, basename='availabilities')
router.register('appointments', AppointmentViewSet, basename='appointments')
router.register('prescriptions', PrescriptionViewSet, basename='prescriptions')
router.register('form-assessment-questions', FormAssessmentQuestionViewSet, basename='form-assessment-questions')
router.register('medicines', MedicineViewSet, basename='medicines')
router.register('recommendedvacines', RecommendedVaccineViewSet, basename='recommendedvacines')
router.register('form-assessments', FormAssessmentViewSet, basename='form-assessments')
router.register('orders', OrderViewSet, basename='orders')
router.register('invoices', InvoiceViewSet, basename='invoices')
router.register('pharmacies', PharmacyViewSet, basename='pharmacies')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
