from drf_spectacular.utils import OpenApiExample

# ─── AUTH ─────────────────────────────────────────────────────

BUYER_REGISTER_REQUEST = OpenApiExample(
    'Buyer Registration',
    value={
        'full_name': 'John Doe',
        'email': 'buyer@example.com',
        'phone': '+1234567890',
        'password': 'StrongPassword123!'
    },
    request_only=True
)

AGENT_REGISTER_REQUEST = OpenApiExample(
    'Agent Registration',
    value={
        'full_name': 'Alice Agent',
        'email': 'agent@agency.com',
        'phone': '+1987654321',
        'password': 'StrongPassword123!',
        'brand_name': 'Luxury Estates',
        'website': 'https://luxuryestates.com'
    },
    request_only=True
)

LOGIN_REQUEST = OpenApiExample(
    'Login Request',
    value={
        'email': 'buyer@example.com',
        'password': 'StrongPassword123!'
    },
    request_only=True
)

LOGIN_RESPONSE = OpenApiExample(
    'Login Response',
    value={
        'refresh': 'eyJ0eXAi...',
        'access': 'eyJ0eXAi...',
        'user': {
            'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'email': 'buyer@example.com',
            'full_name': 'John Doe',
            'role': 'buyer'
        }
    },
    response_only=True
)

# ─── PROPERTIES ───────────────────────────────────────────────

PROPERTY_CREATE_REQUEST = OpenApiExample(
    'Create Property',
    value={
        'title': 'Modern Villa with Sea View',
        'property_type': 'villa',
        'price': '450000.00',
        'address': '123 Ocean Drive, Miami',
        'postcode': '33139',
        'status': 'sale',
        'beds': 4,
        'baths': 3,
        'size_sqft': 2500,
        'lat': 25.7617,
        'lon': -80.1918,
        'description': 'Beautiful fully furnished villa...'
    },
    request_only=True
)

PROPERTY_RESPONSE = OpenApiExample(
    'Property Detail',
    value={
        'id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'title': 'Modern Villa',
        'price': '450000.00',
        'images': [
            {'id': 1, 'image': 'http://.../img.jpg', 'is_cover': True}
        ],
        'agent': {
            'id': '...',
            'full_name': 'Alice Agent',
            'email': 'agent@agency.com'
        }
    },
    response_only=True
)

# ─── OFFERS ───────────────────────────────────────────────────

OFFER_CREATE_REQUEST = OpenApiExample(
    'Submit Offer',
    value={
        'property': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'offer_amount': '440000.00',
        'message': 'We love the kitchen!',
        'buyer_name': 'John Doe',
        'buyer_email': 'buyer@example.com',
        'buyer_phone': '+1234567890'
    },
    request_only=True
)

COUNTER_OFFER_REQUEST = OpenApiExample(
    'Counter Offer',
    value={
        'amount': '445000.00',
        'message': 'We can meet in the middle.'
    },
    request_only=True
)

# ─── QR BOARDS ────────────────────────────────────────────────

REASSIGN_BOARD_REQUEST = OpenApiExample(
    'Reassign Board',
    value={
        'property_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    },
    request_only=True
)

# ─── BOOKINGS ─────────────────────────────────────────────────

BOOKING_CREATE_REQUEST = OpenApiExample(
    'Create Booking',
    value={
        'property': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        'date': '2023-12-25',
        'time_slot': '14:00',
        'message': 'Is it okay if I bring my architect?'
    },
    request_only=True
)
