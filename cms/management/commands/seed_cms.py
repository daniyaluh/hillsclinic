from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = 'Run the CMS seeding commands needed for the public site.'

    def handle(self, *args, **options):
        commands = [
            'setup_homepage',
            'setup_doctors',
            'setup_blog',
        ]

        for cmd in commands:
            try:
                self.stdout.write(f"--> Running {cmd}...")
                management.call_command(cmd)
                self.stdout.write(self.style.SUCCESS(f"    {cmd} completed successfully"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    {cmd} failed: {e}"))
                import traceback
                self.stdout.write(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS('CMS seeding finished.'))
