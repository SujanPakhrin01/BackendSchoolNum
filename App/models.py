from django.db import models


class Gallery(models.Model):
    image = models.ImageField(upload_to="gallery_images/")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Gallery Image {self.id}"


class Admission(models.Model):
    PROGRAM_CHOICES = [
        ("school", "School Programme"),
        ("plus_two", "+2 Programme"),
    ]

    program_type = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True)

    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    available_seats = models.PositiveIntegerField(default=0)
    session = models.CharField(max_length=20)

    required_documents = models.JSONField(default=list, blank=True)
    is_open = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Admission"
        verbose_name_plural = "Admissions"
        ordering = ["deadline"]

    def __str__(self):
        return f"{self.title} ({self.session})"


class AdmissionTeacher(models.Model):
    admission = models.ForeignKey(
        Admission,
        on_delete=models.CASCADE,
        related_name="teachers"
    )

    initials = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=120)

    role = models.CharField(max_length=120, blank=True)
    subject_or_stream = models.CharField(max_length=120, blank=True)
    grade_info = models.CharField(max_length=120, blank=True)
    availability = models.CharField(max_length=120, blank=True)

    phone = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.name} - {self.admission.title}"