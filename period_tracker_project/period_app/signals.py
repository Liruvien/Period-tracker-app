from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=settings.AUTH_USER_MODEL)
def checker(sender, instance, **kwargs):
    if instance.id is None:
        pass
    else:
        current = instance
        previous = UserProfile.objects.get(id=instance.id)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.userprofile.save()


