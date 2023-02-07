from django.core.management.base import BaseCommand
from login.tasks import send_email_alerts

class Command(BaseCommand):
    help = "Send email alerts to users."

    def handle_noargs(self, **options):
        send_email_alerts()
        self.stdout.write('Successfully completed.')

    def handle(self, **options):
        send_email_alerts()
        self.stdout.write('Successfully completed.')

"""
Run this as follows: 
python manage.py email_alerts <ENTER>
"""

