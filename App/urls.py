# App/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GalleryViewSet, AdmissionViewSet, NoticeViewSet, AdmissionTeacherViewSet

router = DefaultRouter()
router.register(r'Gallery', GalleryViewSet)
router.register(r'Admissions', AdmissionViewSet)
router.register(r'Notices', NoticeViewSet)
router.register(r'Teachers', AdmissionTeacherViewSet)

urlpatterns = [
    path('', include(router.urls)),
]