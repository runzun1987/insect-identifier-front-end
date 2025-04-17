import base64
import io

from PIL import Image

def convert_image_bytes_to_base64(base64_str: str, max_size=(1024, 1024)) -> str:
    """
        Decode a base64-encoded image, resize it to fit within max_size,
        convert it to RGB JPEG, and return it as a base64-encoded JPEG string.
        """
    try:
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        image.save(output, format="JPEG")
        image_bytes = output.getvalue()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        return "data:image/jpeg;base64," + base64_image
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")