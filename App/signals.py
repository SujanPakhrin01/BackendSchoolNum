from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notice
from .utils import convert_image_to_pdf


@receiver(post_save, sender=Notice)
def auto_convert_image_to_pdf(sender, instance, created, **kwargs):
    if instance.attachment and instance.is_image() and not instance.converted_pdf:
        instance.attachment.seek(0)
        pdf_file = convert_image_to_pdf(instance.attachment)
        Notice.objects.filter(pk=instance.pk).update(converted_pdf=None)
        instance.converted_pdf.save(pdf_file.name, pdf_file, save=True)