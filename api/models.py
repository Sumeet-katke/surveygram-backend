from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomAccountManage
# Create your models here.
class role(models.Model):

    id = models.IntegerField(unique=True, primary_key=True)
    role_name = models.CharField(max_length=30)
    def __str__(self) -> str:
        return str(self.id)
    

class CustomUser (AbstractUser):
    username = None
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length= 50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    userId = models.CharField(max_length=50, unique=True)
    roleId = models.ForeignKey(role, on_delete=models.CASCADE, default=3)
    objects=CustomAccountManage()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

