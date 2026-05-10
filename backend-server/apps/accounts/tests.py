from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import OTPVerification
from .services import AuthService


User = get_user_model()


class PasswordResetOtpTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='selim.reza.uits@gmail.com',
			password='StrongPass123',
			full_name='Selim Reza',
		)

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_send_otp_trims_and_lowercases_email_and_sends_mail(self):
		code = AuthService.send_otp('  SRREZA1999@gmail.com  ')

		self.assertEqual(len(code), 4)
		self.assertEqual(OTPVerification.objects.count(), 1)
		otp = OTPVerification.objects.get()
		self.assertEqual(otp.email, 'srreza1999@gmail.com')
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].to, ['srreza1999@gmail.com'])

	def test_verify_otp_is_case_insensitive_for_email(self):
		otp = OTPVerification.objects.create(
			email='selim.reza.uits@gmail.com',
			otp_code='1234',
			expires_at=timezone.now() + timezone.timedelta(minutes=10),
		)

		self.assertTrue(AuthService.verify_otp('SELIM.REZA.UITS@GMAIL.COM', otp.otp_code, consume=False))
