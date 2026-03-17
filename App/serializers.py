from rest_framework import serializers
from .models import Gallery, Admission, AdmissionTeacher


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