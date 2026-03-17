from PIL import Image
from django.core.files.base import ContentFile
import io


def convert_image_to_pdf(image_file):
    """
    Converts an uploaded image file to PDF.
    Returns a ContentFile containing the PDF bytes.
    """
    image = Image.open(image_file)

    # Convert to RGB if necessary (e.g., PNG with transparency)
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')

    pdf_buffer = io.BytesIO()
    image.save(pdf_buffer, format='PDF', resolution=100.0)
    pdf_buffer.seek(0)

    # Build output filename
    original_name = getattr(image_file, 'name', 'attachment')
    pdf_name = original_name.rsplit('.', 1)[0] + '.pdf'

    return ContentFile(pdf_buffer.read(), name=pdf_name)