from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.BooleanField(default = 0) 
    name = models.CharField(max_length = 200, default = "NULL")

    weight = models.FloatField(default = 60.0) 
    height = models.FloatField(default = 170.0) 

    allergies = models.JSONField(default = list) 
    diagnoses = models.JSONField(default = list) 
    medications = models.JSONField(default = list)

    history = models.JSONField(default = list)
    upcoming = models.JSONField(default = list)

    address = models.TextField(default="Not set") 
    country = "Canada" 
    city = models.TextField(default = "Not set")
    province = models.TextField(default = "Not set")
    postalcode = models.CharField(max_length=6, default = "XXXXXX")

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()