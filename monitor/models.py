from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
import logging
# Existing Warning model
class Warning(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.timestamp}: {self.message}"

    # Custom table name
    class Meta:
        db_table = 'warnings'

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}" 

          
logger = logging.getLogger(__name__)
# Signal to send email when a new warning is created
@receiver(post_save, sender=Warning)
def send_warning_email(sender, instance, created, **kwargs):
    if created:  # Only send email for newly created warnings
        logger.debug("send_warning_email signal triggered.")  # Debug log to verify signal is triggered
        subject = "Privilege Escalation Attempt Detected"
        message = f"A new warning has been logged:\n\n{instance.message}\n\nTimestamp: {instance.timestamp}"
        from_email = 'anandvaliyakalayil0727@gmail.com'  # Replace with your email address
        recipient_list = ['ananthakrishnan272004@gmail.com']  # Replace with the recipient's email address
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.debug("Email sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email: {e}")





          


