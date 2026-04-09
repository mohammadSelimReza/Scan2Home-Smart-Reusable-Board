from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'List all users in the database'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('id')
        self.stdout.write(self.style.SUCCESS(f"{'ID':<5} | {'Role':<10} | {'Email':<35} | {'Name':<20}"))
        self.stdout.write("-" * 80)
        for user in users:
            self.stdout.write(f"{user.id:<5} | {user.role:<10} | {user.email:<35} | {user.full_name:<20}")
