from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (GalleryViewSet,AdmissionViewSet,AdmissionTeacherViewSet)

router = DefaultRouter()
router.register(r'Gallery', GalleryViewSet)
router.register(r'Admissions', AdmissionViewSet)
router.register(r'Teachers', AdmissionTeacherViewSet)

urlpatterns = [
    path('', include(router.urls)),
]