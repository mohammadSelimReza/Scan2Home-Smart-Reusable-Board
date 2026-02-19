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

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=200, help='Total properties to create')

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Populating database with ~{count} records...')

        # 1. Create Agents
        agents = []
        for i in range(10):
            email = f'agent{i}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': f'Agent {i}',
                    'phone': f'+100000000{i}',
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
                    'brand_name': f'Luxury Agency {i}',
                    'website': f'https://agency{i}.com',
                    'is_verified': True
                }
            )
            agents.append(user)

        # 2. Create Buyers
        buyers = []
        for i in range(20):
            email = f'buyer{i}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': f'Buyer {i}',
                    'phone': f'+200000000{i}',
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
        
        for i in range(count):
            agent = random.choice(agents)
            p_type = random.choice(property_types)
            status = random.choice(statuses)
            
            prop = Property.objects.create(
                agent=agent,
                title=f'Beautiful {p_type.capitalize()} {i}',
                property_type=p_type,
                price=random.randint(100000, 1000000),
                address=f'{i} Real State Street, City',
                postcode=f'ABC{i}',
                status=status,
                description=f'Experience luxury living in this {p_type}. Great amenities and view.',
                beds=random.randint(1, 6),
                baths=random.randint(1, 4),
                size_sqft=random.randint(500, 5000),
                is_approved=True,
                is_featured=random.choice([True, False])
            )
            properties.append(prop)

        # 4. Create QR Boards
        for i in range(min(50, count)):
            prop = properties[i]
            board = QRBoard.objects.create(agent=prop.agent)
            BoardAssignment.objects.create(board=board, property=prop, is_active=True)

        # 5. Create Offers
        offer_statuses = ['pending', 'accepted', 'rejected']
        for i in range(min(100, count)):
            prop = random.choice(properties)
            buyer_user = random.choice(buyers)
            
            offer = Offer.objects.create(
                property=prop,
                buyer=buyer_user,
                buyer_name=buyer_user.full_name,
                email=buyer_user.email,
                phone=buyer_user.phone,
                offer_amount=prop.price * random.uniform(0.9, 1.1),
                message="I'm very interested!",
                status=random.choice(offer_statuses)
            )
            
            if random.choice([True, False]):
                CounterOffer.objects.create(
                    offer=offer,
                    amount=offer.offer_amount * 1.05,
                    message="How about this?",
                    by_agent=True
                )

        # 6. Create Bookings
        for i in range(min(100, count)):
            prop = random.choice(properties)
            buyer = random.choice(buyers)
            Booking.objects.create(
                property=prop,
                buyer=buyer,
                date=timezone.now().date() + timezone.timedelta(days=random.randint(1, 30)),
                time_slot="14:00",
                message="Checking the neighborhood."
            )

        # 7. Create Support Messages
        for i in range(20):
            user = random.choice(buyers + agents)
            SupportMessage.objects.create(
                user=user,
                message=f"Need help with my account {i}."
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully populated dummy data.'))
