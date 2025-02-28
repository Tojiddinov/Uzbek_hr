from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobSeekerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_job_seeker_profile(sender, instance, created, **kwargs):
    if created and instance.role == "job_seeker":  # Faqat Job Seeker uchun profil yaratish
        JobSeekerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_job_seeker_profile(sender, instance, **kwargs):
    if hasattr(instance, "job_seeker_profile"):
        instance.job_seeker_profile.save()
