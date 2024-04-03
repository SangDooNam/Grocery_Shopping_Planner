from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


class Profile(AbstractUser):
    
    photo = models.ImageField(upload_to='profile_photo', default= 'profile_photo/default.jpg')
    website = models.URLField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    biografie = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    birthday_date = models.DateField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.username
    