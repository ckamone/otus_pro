from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class CustomUser(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images/', blank=True, default='images/default.png',)

    def __str__(self) -> str:
        return self.user.username