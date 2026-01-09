from django.test import TestCase
from django.core import mail
from unittest.mock import patch

from testing.models import User


class TestTestingSignals(TestCase):

    def test_user_created_signal_sends_welcome_email(self):
        """Test that creating a user sends a welcome email."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        # Check the email subject
        self.assertEqual(mail.outbox[0].subject, "Welcome to Our Platform!")
        # Check the recipient
        self.assertIn('test@example.com', mail.outbox[0].to)

    def test_user_created_signal_multiple_users(self):
        """Test that each new user gets a welcome email."""
        for i in range(3):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='pass123'
            )
        # 3 users = 3 emails
        self.assertEqual(len(mail.outbox), 3)

    def test_user_update_does_not_send_email(self):
        """Test that updating a user does NOT send another email."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        # 1 email from creation
        self.assertEqual(len(mail.outbox), 1)

        # Update the user
        user.first_name = "Updated"
        user.save()

        # Still only 1 email (no new email on update)
        self.assertEqual(len(mail.outbox), 1)

    @patch('testing.signals.send_mail')
    def test_user_created_signal_calls_send_mail(self, mock_send_mail):
        """Test that send_mail is called with correct arguments."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        mock_send_mail.assert_called_once_with(
            subject="Welcome to Our Platform!",
            message="Thank you for registering.",
            from_email="admin@django.com",
            recipient_list=['test@example.com'],
            fail_silently=False
        )
