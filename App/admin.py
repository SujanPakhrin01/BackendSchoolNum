from django.contrib import admin
from .models import Gallery, Admission, AdmissionTeacher,Notice


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
    

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_at", "file_type"]
    search_fields = ["title", "content"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]

    def file_type(self, obj):
        if obj.is_image():
            return "Image"
        elif obj.attachment:
            return "File"
        return "No File"

    file_type.short_description = "Attachment Type"