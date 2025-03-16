import uuid
import base64
from django.core.files.base import ContentFile


def get_formatted_image(initial_name, image):
    image_format, image_str = image.split(';base64,')
    format_ext = image_format.split('/')[-1]
    image_name = f'{initial_name}{uuid.uuid4()}.'
    formated_image = ContentFile(base64.b64decode(image_str), name=image_name + format_ext)
    return formated_image
