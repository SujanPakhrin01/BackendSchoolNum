from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GalleryViewSet,
    AdmissionViewSet,
    AdmissionTeacherViewSet
)

router = DefaultRouter()
router.register(r'gallery', GalleryViewSet)
router.register(r'admissions', AdmissionViewSet)
router.register(r'teachers', AdmissionTeacherViewSet)

urlpatterns = [
    path('', include(router.urls)),
]