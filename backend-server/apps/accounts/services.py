import random
import string
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from .models import OTPVerification

OTP_EXPIRY = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)


class AuthService:
    @staticmethod
    def generate_otp(length: int = 4) -> str:
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_otp(email: str) -> str:
        """Generate OTP, save to DB, send via email. Returns the code."""
        # Invalidate old OTPs
        OTPVerification.objects.filter(email=email, is_used=False).update(is_used=True)

        code = AuthService.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY)
        OTPVerification.objects.create(
            email=email,
            otp_code=code,
            expires_at=expires_at,
        )

        send_mail(
            subject='Scan2Home — Password Reset OTP',
            message=f'Your OTP is: {code}\nIt expires in {OTP_EXPIRY} minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return code

    @staticmethod
    def verify_otp(email: str, code: str,consume: bool = True) -> bool:
        """Returns True if valid, marks as used."""
        otp = OTPVerification.objects.filter(
            email=email,
            otp_code=code,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()
        if otp:
            if consume:
                otp.is_used = True
                otp.save()
            return True
        return False
