from django.core.files.storage import Storage


class NullStorage(Storage):
    """A no-op storage backend that accepts files but doesn't store them.

    Use for WAGTAILIMAGES_RENDITION_STORAGE when you want to ensure
    renditions are not persisted anywhere (suitable for ephemeral hosts).
    """
    def _open(self, name, mode='rb'):
        raise FileNotFoundError

    def _save(self, name, content):
        # Pretend we saved by returning the name; do not write to disk
        return name

    def exists(self, name):
        return False

    def url(self, name):
        # No URL for renditions; callers should use Cloudinary URLs instead
        return ''

    def size(self, name):
        return 0

    def delete(self, name):
        return None
