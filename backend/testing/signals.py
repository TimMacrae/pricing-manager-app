from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created: bool, **kwargs):
    """
    Signal receiver to send a welcome email when a new User is created.

    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: A boolean; True if a new record was created
        **kwargs: Additional keyword arguments
    """
    if created:
        # Logic to send welcome email
        send_mail(
            subject="Welcome to Our Platform!",
            message="Thank you for registering.",
            from_email="admin@django.com",
            recipient_list=[instance.email],
            fail_silently=False
        )
