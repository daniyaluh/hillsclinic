from django.core.mail import send_mail
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email to verify SMTP delivery"

    def add_arguments(self, parser):
        parser.add_argument("to", nargs="?", help="Recipient email address")
        parser.add_argument(
            "--subject",
            default="Hills Clinic • SMTP Test",
            help="Email subject",
        )
        parser.add_argument(
            "--body",
            default=(
                "This is a test email from Hills Clinic.\n\n"
                "If you are reading this in your inbox, SMTP is working."
            ),
            help="Email body",
        )

    def handle(self, *args, **options):
        to = options.get("to")
        subject = options.get("subject")
        body = options.get("body")

        if not to:
            raise CommandError("Please provide a recipient: manage.py send_test_email <email>")

        self.stdout.write(self.style.WARNING(f"Sending test email to {to} ..."))
        sent = send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to],
            fail_silently=False,
        )

        if sent:
            self.stdout.write(self.style.SUCCESS("Email queued/sent successfully."))
        else:
            raise CommandError("Email sending failed.")
