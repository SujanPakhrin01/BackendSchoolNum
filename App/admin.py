from django.contrib import admin
from .models import Gallery, Admission, AdmissionTeacher


class AdmissionTeacherInline(admin.TabularInline):
    model = AdmissionTeacher
    extra = 1


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "program_type", "session", "deadline", "is_open")
    list_filter = ("program_type", "is_open", "session")
    search_fields = ("title", "session")
    inlines = [AdmissionTeacherInline]


@admin.register(AdmissionTeacher)
class AdmissionTeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "admission", "phone", "display_order")
    search_fields = ("name", "phone")


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "image")