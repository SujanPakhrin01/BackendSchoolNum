from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Gallery, Admission, AdmissionTeacher
from .serializers import (
    GallerySerializer,
    AdmissionSerializer,
    AdmissionWriteSerializer,
    AdmissionTeacherSerializer
)


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by("-updated_at")
    serializer_class = GallerySerializer
    
    


class AdmissionViewSet(viewsets.ModelViewSet):
    queryset = Admission.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AdmissionWriteSerializer
        return AdmissionSerializer

    @action(detail=False, methods=["get"])
    def open(self, request):
        """Get only open admissions"""
        queryset = Admission.objects.filter(is_open=True)
        serializer = AdmissionSerializer(queryset, many=True)
        return Response(serializer.data)


class AdmissionTeacherViewSet(viewsets.ModelViewSet):
    queryset = AdmissionTeacher.objects.all()
    serializer_class = AdmissionTeacherSerializer