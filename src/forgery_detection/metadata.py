from pathlib import Path

from PIL import Image


class MetadataAnalyzer:
    """
    Extract basic image metadata.

    Metadata is only a supporting forensic signal.
    Missing metadata does NOT mean an image is forged.
    """

    def analyze(self, image):
        if isinstance(image, (str, Path)):
            image_path = Path(image)

            if not image_path.exists():
                raise FileNotFoundError(
                    f"Image not found: {image_path}"
                )

            try:
                with Image.open(image_path) as img:
                    metadata = dict(img.getexif())
                    width, height = img.size
                    image_format = img.format
                    mode = img.mode

                return {
                    "status": "completed",
                    "format": image_format,
                    "mode": mode,
                    "width": width,
                    "height": height,
                    "metadata_count": len(metadata),
                    "has_metadata": len(metadata) > 0,
                }

            except Exception as exc:
                return {
                    "status": "error",
                    "error": str(exc),
                }

        return {
            "status": "not_available",
            "message": "Metadata analysis requires an image file path.",
        }


def run_check(image):
    """Compatibility helper."""
    return MetadataAnalyzer().analyze(image)
