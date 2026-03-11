import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from apps.accounts.models import AgentProfile
from apps.properties.models import Property, PropertyImage
from apps.offers.models import Offer
from apps.bookings.models import Booking
from apps.qr_boards.models import QRBoard
from apps.notifications.models import Notification, NotificationType

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with fake admin, 10 users, 4 agents, and interconnecting dummy data'

    def handle(self, *args, **kwargs):
        fake = Faker('en_GB')
        self.stdout.write("Starting database seeding...")

        # 1. Create Admin
        admin_email = "admin@admin.com"
        admin_pass = "123"
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=admin_pass,
                first_name="Super",
                last_name="Admin",
            )
            self.stdout.write(self.style.SUCCESS(f"Created Admin: {admin_email} / {admin_pass}"))
        else:
            self.stdout.write(f"Admin {admin_email} already exists.")

        # Shared password
        test_pass = "test_pass_123"

        # 2. Create 10 Users (Buyers)
        users = []
        for i in range(10):
            email = f"user{i+1}@dummy.com"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'phone_number': fake.phone_number()[:15],
                    'user_type': User.UserType.USER,
                }
            )
            if created:
                user.set_password(test_pass)
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS("Ensured 10 regular users exist."))

        # 3. Create 4 Agents
        agents = []
        for i in range(4):
            email = f"agent{i+1}@dummy.com"
            agent, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'phone_number': fake.phone_number()[:15],
                    'user_type': User.UserType.AGENT,
                }
            )
            if created:
                agent.set_password(test_pass)
                agent.save()
                
            AgentProfile.objects.get_or_create(
                user=agent,
                defaults={
                    'agency_name': fake.company(),
                    'bio': fake.text(max_nb_chars=200),
                    'license_number': fake.bothify(text='LIC-########'),
                    'facebook_url': fake.url(),
                    'instagram_url': fake.url(),
                    'linkedin_url': fake.url(),
                }
            )
            agents.append(agent)
        self.stdout.write(self.style.SUCCESS("Ensured 4 agents exist."))

        # 4. Create dummy properties for agents
        properties = []
        for agent in agents:
            # 3 properties per agent
            for _ in range(3):
                prop = Property.objects.create(
                    agent=agent,
                    title=fake.catch_phrase(),
                    description=fake.paragraph(nb_sentences=5),
                    property_type=random.choice(['apartment', 'house', 'condo', 'townhouse']),
                    listing_type=random.choice(['sale', 'rent']),
                    price=Decimal(random.randint(150000, 850000)),
                    address=fake.street_address(),
                    city=fake.city(),
                    state=fake.county(),
                    zip_code=fake.postcode(),
                    country='UK',
                    bedrooms=random.randint(1, 5),
                    bathrooms=random.randint(1, 4),
                    square_foot=random.randint(500, 3000),
                    status=random.choice(['active', 'under_offer', 'sold']),
                    views_count=random.randint(0, 150),
                    qr_scanned_count=random.randint(0, 75),
                )
                properties.append(prop)

        self.stdout.write(self.style.SUCCESS(f"Created {len(properties)} properties."))

        # 5. Create Offers and Bookings from users -> properties
        for prop in properties:
            # Random 0-3 offers per property
            for _ in range(random.randint(0, 3)):
                buyer = random.choice(users)
                Offer.objects.create(
                    property=prop,
                    buyer_name=buyer.get_full_name(),
                    buyer_email=buyer.email,
                    buyer_phone=buyer.phone_number,
                    offer_amount=prop.price * Decimal(random.uniform(0.9, 1.1)),
                    message=fake.text(max_nb_chars=100),
                    status=random.choice(['pending', 'accepted', 'rejected']),
                )

            # Random 0-2 bookings per property
            for _ in range(random.randint(0, 2)):
                buyer = random.choice(users)
                Booking.objects.create(
                    property=prop,
                    buyer=buyer,
                    booking_date=timezone.now().date() + timezone.timedelta(days=random.randint(1, 14)),
                    booking_time=timezone.now().time(),
                    message=fake.text(max_nb_chars=100),
                    status=random.choice(['pending', 'confirmed', 'cancelled']),
                )
                
            # Random 0-1 QR boards per property
            if random.choice([True, False]):
                QRBoard.objects.create(
                    property=prop,
                    agent=prop.agent,
                    board_id=fake.uuid4()[:8],
                    qr_code_url=fake.url(),
                    status='active',
                )
                
        self.stdout.write(self.style.SUCCESS("Created Offers, Bookings, and QR Boards."))

        # 6. Generate some notifications
        for agent in agents:
            for _ in range(random.randint(3, 8)):
                Notification.objects.create(
                    user=agent,
                    title=fake.sentence(nb_words=4),
                    body=fake.sentence(nb_words=10),
                    notification_type=random.choice(['offer', 'booking', 'qr_scan', 'property']),
                    is_read=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))

        self.stdout.write("\n=== SEEDED ACCOUNTS ===")
        self.stdout.write("Admin: admin@admin.com / 123")
        self.stdout.write("Users: user1@dummy.com ... user10@dummy.com (password: test_pass_123)")
        self.stdout.write("Agents: agent1@dummy.com ... agent4@dummy.com (password: test_pass_123)")
        self.stdout.write("=" * 23)
