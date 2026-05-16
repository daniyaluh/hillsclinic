"""
Delete Cloudinary rendition assets while preserving original uploads.
"""
import os

from django.core.management.base import BaseCommand

import cloudinary
import cloudinary.api
import cloudinary.uploader


class Command(BaseCommand):
    help = "Delete Cloudinary rendition assets and keep originals"

    rendition_markers = (
        ".fill-",
        ".width-",
        ".max-",
        ".crop-",
        ".scale-",
        ".format-",
        ".2e16d0ba.",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually delete matching renditions. Without this flag the command only lists matches.",
        )

    def _is_rendition(self, public_id):
        normalized = public_id.lower()
        return any(marker in normalized for marker in self.rendition_markers)

    def handle(self, *args, **options):
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not cloud_name or not api_key or not api_secret:
            self.stdout.write(self.style.ERROR("Cloudinary credentials are not fully set."))
            return

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        try:
            response = cloudinary.api.resources(max_results=500, resource_type="image", type="upload")
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to read Cloudinary assets: {exc}"))
            return

        resources = response.get("resources", []) if isinstance(response, dict) else []
        matches = [resource for resource in resources if self._is_rendition(resource.get("public_id", ""))]

        self.stdout.write(f"Found {len(resources)} total Cloudinary assets")
        self.stdout.write(f"Found {len(matches)} rendition assets to delete")

        if not matches:
            return

        if not options["apply"]:
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --apply to delete renditions."))
            for resource in matches:
                self.stdout.write(f"- {resource.get('public_id', '')}")
            return

        deleted = 0
        for resource in matches:
            public_id = resource.get("public_id", "")
            if not public_id:
                continue

            try:
                result = cloudinary.uploader.destroy(
                    public_id,
                    resource_type="image",
                    type="upload",
                    invalidate=True,
                )
                if result.get("result") in {"ok", "not found"}:
                    deleted += 1
                    self.stdout.write(self.style.SUCCESS(f"Deleted: {public_id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped: {public_id} -> {result}"))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"Failed to delete {public_id}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted}/{len(matches)} rendition assets."))
