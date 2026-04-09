import random
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import AgentProfile
from apps.properties.models import Property, PropertyImage, SupportMessage
from apps.qr_boards.models import QRBoard, BoardAssignment
from apps.offers.models import Offer, CounterOffer
from apps.bookings.models import Booking
from faker import Faker

User = get_user_model()
fake = Faker('en_GB')

class Command(BaseCommand):
    help = 'Populates the database with realistic dummy data using Faker for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=200, help='Total properties to create')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Populating database with ~{count} realistic records...')

        # 0. Create standard demo accounts
        # Admin Demo
        admin_email = 'admin@scan2home.co.uk'
        admin_pw = 'password123'
        admin_user, _ = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'full_name': 'System Admin',
                'role': 'admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password(admin_pw)
        admin_user.save()

        # Agent Demo
        agent_demo_email = 'agent@scan2home.co.uk'
        agent_demo_pw = 'password123'
        agent_demo_user, _ = User.objects.get_or_create(
            email=agent_demo_email,
            defaults={
                'full_name': 'Demo Agent',
                'phone': '+447000000001',
                'role': 'agent',
                'is_active': True
            }
        )
        agent_demo_user.set_password(agent_demo_pw)
        agent_demo_user.save()
        AgentProfile.objects.get_or_create(
            user=agent_demo_user,
            defaults={
                'brand_name': 'Premium UK Estates',
                'website': 'https://premium-uk-estates.com',
                'is_verified': True
            }
        )

        # Buyer Demo
        buyer_demo_email = 'buyer@scan2home.co.uk'
        buyer_demo_pw = 'password123'
        buyer_demo_user, _ = User.objects.get_or_create(
            email=buyer_demo_email,
            defaults={
                'full_name': 'Demo Buyer',
                'phone': '+447000000002',
                'role': 'buyer',
                'is_active': True
            }
        )
        buyer_demo_user.set_password(buyer_demo_pw)
        buyer_demo_user.save()


        # 1. Create Extra Agents
        agents = [agent_demo_user]
        for _ in range(9):
            email = fake.unique.email()
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': fake.name(),
                    'phone': fake.phone_number()[:15],
                    'role': 'agent',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            profile, _ = AgentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'brand_name': fake.company(),
                    'website': fake.url(),
                    'is_verified': True
                }
            )
            agents.append(user)

        # 2. Create Extra Buyers
        buyers = [buyer_demo_user]
        for _ in range(19):
            email = fake.unique.email()
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': fake.name(),
                    'phone': fake.phone_number()[:15],
                    'role': 'buyer',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            buyers.append(user)

        # 3. Create Properties
        property_types = ['house', 'apartment', 'villa']
        statuses = ['available', 'under_offer', 'sold']
        properties = []
        
        for _ in range(count):
            agent = random.choice(agents)
            p_type = random.choice(property_types)
            status = random.choice(statuses)
            
            # Generate realistic features/descriptions
            descriptors = ['Beautiful', 'Stunning', 'Modern', 'Classic', 'Spacious', 'Charming']
            title = f"{random.choice(descriptors)} {fake.street_name()} {p_type.capitalize()}"
            
            prop = Property.objects.create(
                agent=agent,
                title=title,
                property_type=p_type,
                price=random.randint(150000, 2500000),
                address=fake.street_address() + ', ' + fake.city(),
                postcode=fake.postcode(),
                status=status,
                description=fake.paragraph(nb_sentences=5),
                beds=random.randint(1, 6),
                baths=random.randint(1, 4),
                size_sqft=random.randint(500, 5000),
                is_approved=True,
                is_featured=random.choice([True, False, False, False]) # 25% featured
            )
            properties.append(prop)

        # 4. Create QR Boards
        for i in range(min(50, count)):
            prop = properties[i]
            board = QRBoard.objects.create(agent=prop.agent)
            BoardAssignment.objects.create(board=board, property=prop, is_active=True)

        # 5. Create Offers
        offer_statuses = ['pending', 'accepted', 'rejected']
        for _ in range(min(100, count)):
            prop = random.choice(properties)
            buyer_user = random.choice(buyers)
            
            offer = Offer.objects.create(
                property=prop,
                buyer=buyer_user,
                buyer_name=buyer_user.full_name,
                email=buyer_user.email,
                phone=buyer_user.phone,
                offer_amount=prop.price * random.uniform(0.9, 1.1),
                message=fake.sentence(),
                status=random.choice(offer_statuses)
            )
            
            if random.choice([True, False]):
                CounterOffer.objects.create(
                    offer=offer,
                    amount=offer.offer_amount * 1.05,
                    message=fake.sentence(),
                    by_agent=True
                )

        # 6. Create Bookings
        for _ in range(min(100, count)):
            prop = random.choice(properties)
            buyer = random.choice(buyers)
            
            # Select a random timeslot roughly within business hours
            hour = random.randint(9, 17)
            time_slot = f"{hour:02d}:00"

            Booking.objects.create(
                property=prop,
                buyer=buyer,
                date=timezone.now().date() + timezone.timedelta(days=random.randint(1, 30)),
                time_slot=time_slot,
                message=fake.sentence()
            )

        # 7. Create Support Messages
        for _ in range(20):
            user = random.choice(buyers + agents)
            SupportMessage.objects.create(
                user=user,
                message=fake.paragraph(nb_sentences=2)
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated realistic dummy data.'))
        self.stdout.write(self.style.SUCCESS('---------- DEMO CREDENTIALS ----------'))
        self.stdout.write(self.style.WARNING(f'Admin: {admin_email} | Password: {admin_pw}'))
        self.stdout.write(self.style.WARNING(f'Agent: {agent_demo_email} | Password: {agent_demo_pw}'))
        self.stdout.write(self.style.WARNING(f'Buyer: {buyer_demo_email} | Password: {buyer_demo_pw}'))
        self.stdout.write(self.style.SUCCESS('--------------------------------------'))
