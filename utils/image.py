import base64
import io

from PIL import Image


def convert_image_bytes_to_base64(image_bytes: bytes, max_size=(1024, 1024)) -> str:
    """
    Accept raw image bytes, resize the image to fit within max_size,
    convert it to RGB JPEG, and return it as a base64-encoded JPEG string.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        image.save(output, format="JPEG")
        base64_image = base64.b64encode(output.getvalue()).decode("utf-8")

        return "data:image/jpeg;base64," + base64_image
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")
