"""Template tags to build Cloudinary URLs without creating Wagtail renditions.

Using these tags prevents Wagtail from generating and saving renditions to
`WAGTAILIMAGES_RENDITION_STORAGE`. Instead the tag builds a Cloudinary URL
that applies transformations on-demand at delivery time.
"""
from django import template
import cloudinary.utils
import os

register = template.Library()


def _get_public_id(image):
    """Extract public_id from a Wagtail Image or a FileField-like object."""
    if not image:
        return None

    # Wagtail Image instance has `.file.name`; a FileField or string may be used too
    file_name = None
    try:
        file_name = image.file.name
    except Exception:
        try:
            file_name = str(image)
        except Exception:
            return None

    # Remove extension
    if '.' in file_name:
        public_id = file_name.rsplit('.', 1)[0]
    else:
        public_id = file_name

    # Cloudinary expects forward-slash separated public ids; keep as-is
    return public_id


@register.simple_tag
def cloudinary_url(image, width=None, height=None, crop=None, fmt=None, quality=None):
    """Return a Cloudinary URL for `image` applying optional transformations.

    Usage examples in templates:
      {% cloudinary_url page.hero_image width=800 as hero_url %}
      <img src="{{ hero_url }}">

    The tag intentionally does not call Wagtail's rendition APIs so no
    renditions are created or saved.
    """
    public_id = _get_public_id(image)
    if not public_id:
        return ''

    transformation = {}
    if width:
        try:
            transformation['width'] = int(width)
        except Exception:
            transformation['width'] = width
    if height:
        try:
            transformation['height'] = int(height)
        except Exception:
            transformation['height'] = height
    if crop:
        transformation['crop'] = crop
    if quality:
        transformation['quality'] = quality

    try:
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            format=fmt,
            transformation=transformation or None,
            secure=True,
        )
        return url
    except Exception:
        # Fallback to a direct Cloudinary delivery URL (no transform)
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME') or ''
        if not cloud_name:
            return ''
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
