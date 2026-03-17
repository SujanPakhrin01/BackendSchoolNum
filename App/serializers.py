from rest_framework import serializers
from .models import Gallery, Admission, AdmissionTeacher,Notice
from .utils import convert_image_to_pdf
import os


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "image"]


class AdmissionTeacherSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    admission_title = serializers.CharField(
        source="admission.title",
        read_only=True
    )

    class Meta:
        model = AdmissionTeacher
        fields = [
            "id",
            "admission",
            "admission_title",
            "initials",
            "name",
            "role",
            "subject_or_stream",
            "grade_info",
            "availability",
            "phone",
            "whatsapp_number",
            "email",
            "display_order",
        ]
        extra_kwargs = {
            "admission": {"write_only": True, "required": False}
        }


class AdmissionSerializer(serializers.ModelSerializer):
    teachers = AdmissionTeacherSerializer(many=True, read_only=True)
    program_type_display = serializers.CharField(
        source="get_program_type_display",
        read_only=True
    )
    teacher_count = serializers.IntegerField(
        source="teachers.count",
        read_only=True
    )

    class Meta:
        model = Admission
        fields = [
            "id",
            "program_type",
            "program_type_display",
            "title",
            "subtitle",
            "monthly_fee",
            "deadline",
            "available_seats",
            "session",
            "required_documents",
            "is_open",
            "created_at",
            "teacher_count",
            "teachers",
        ]


class AdmissionWriteSerializer(serializers.ModelSerializer):
    teachers = AdmissionTeacherSerializer(many=True, required=False)

    class Meta:
        model = Admission
        fields = [
            "id",
            "program_type",
            "title",
            "subtitle",
            "monthly_fee",
            "deadline",
            "available_seats",
            "session",
            "required_documents",
            "is_open",
            "teachers",
        ]

    def create(self, validated_data):
        teachers_data = validated_data.pop("teachers", [])
        admission = Admission.objects.create(**validated_data)

        for teacher_data in teachers_data:
            AdmissionTeacher.objects.create(
                admission=admission,
                **teacher_data
            )

        return admission

    def update(self, instance, validated_data):
        teachers_data = validated_data.pop("teachers", None)

        # update admission fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if teachers_data is not None:
            existing_ids = {t.id for t in instance.teachers.all()}
            kept_ids = set()

            for teacher_data in teachers_data:
                teacher_id = teacher_data.get("id")

                if teacher_id and teacher_id in existing_ids:
                    AdmissionTeacher.objects.filter(id=teacher_id).update(**teacher_data)
                    kept_ids.add(teacher_id)
                else:
                    teacher = AdmissionTeacher.objects.create(
                        admission=instance,
                        **teacher_data
                    )
                    kept_ids.add(teacher.id)

            # delete removed teachers
            instance.teachers.exclude(id__in=kept_ids).delete()

        return instance
    

class NoticeSerializer(serializers.ModelSerializer):
    # Read-only helper fields
    final_pdf        = serializers.SerializerMethodField()
    is_image         = serializers.SerializerMethodField()
    attachment_type  = serializers.SerializerMethodField()   # "image" | "pdf" | null

    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content',
            'attachment', 'converted_pdf',   # raw file fields
            'final_pdf', 'is_image',         # smart helpers
            'attachment_type',               # "image" | "pdf" | null
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'converted_pdf',
                            'final_pdf', 'is_image', 'attachment_type']

    # ── helpers ──────────────────────────────
    def get_final_pdf(self, obj):
        request = self.context.get('request')
        pdf = obj.get_final_pdf()
        if pdf and hasattr(pdf, 'url') and request:
            try:
                return request.build_absolute_uri(pdf.url)
            except Exception:
                return None
        return None

    def get_is_image(self, obj):
        return obj.is_image()

    def get_attachment_type(self, obj):
        if not obj.attachment:
            return None
        ext = os.path.splitext(obj.attachment.name)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        return 'other'

    # ── validation ───────────────────────────
    def validate_attachment(self, value):
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f'Unsupported file. Allowed: {", ".join(valid_extensions)}'
            )
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File must not exceed 10 MB.')
        return value

    # ── image → pdf conversion ───────────────
    def _convert_if_image(self, notice):
        if notice.attachment and notice.is_image() and not notice.converted_pdf:
            from .utils import convert_image_to_pdf
            notice.attachment.seek(0)
            pdf_file = convert_image_to_pdf(notice.attachment)
            notice.converted_pdf.save(pdf_file.name, pdf_file, save=True)

    def create(self, validated_data):
        notice = super().create(validated_data)
        self._convert_if_image(notice)
        return notice

    def update(self, instance, validated_data):
        # If a new attachment is coming in, wipe the old PDF
        if 'attachment' in validated_data and instance.converted_pdf:
            instance.converted_pdf.delete(save=False)
            instance.converted_pdf = None
        instance = super().update(instance, validated_data)
        self._convert_if_image(instance)
        return instance