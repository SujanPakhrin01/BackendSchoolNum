from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notice
from .serializers import NoticeSerializer

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
    
    
class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().order_by('-created_at')
    serializer_class = NoticeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.attachment:
            instance.attachment.delete(save=False)
        if instance.converted_pdf:
            instance.converted_pdf.delete(save=False)
        instance.delete()
        return Response({'message': 'Notice deleted.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'], url_path='remove-attachment')
    def remove_attachment(self, request, pk=None):
        """DELETE /api/notices/<id>/remove-attachment/"""
        notice = self.get_object()
        if notice.attachment:
            notice.attachment.delete(save=False)
            notice.attachment = None
        if notice.converted_pdf:
            notice.converted_pdf.delete(save=False)
            notice.converted_pdf = None
        notice.save()
        return Response(self.get_serializer(notice).data)