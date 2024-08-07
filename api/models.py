from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomAccountManage
# from datetime import datetime
from django.utils import timezone
from datetime import timedelta

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
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    userId = models.CharField(max_length=50, blank=True, null=True)
    roleId = models.ForeignKey(role, on_delete=models.CASCADE, default=3)
    objects=CustomAccountManage()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    isActive = models.BooleanField(default=False)
    url = models.CharField(max_length=400)
    sector = models.CharField(max_length=100)

class rewards(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class typeOfQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, null=False)
    time = models.TimeField(null=False)
    reward = models.IntegerField()

class survey(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40)
    reward = models.ForeignKey(rewards, on_delete=models.PROTECT)
    rewardQuantity = models.IntegerField()
    startDate = models.DateField(default= timezone.now)
    endDate = models.DateField(default= timezone.now() + timedelta(days=7))
    ageFrom = models.IntegerField(default=18)
    ageTo = models.IntegerField(default=35)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    createdTime = models.DateTimeField(default=timezone.now)
    typeOf = models.ForeignKey(typeOfQuestion, on_delete=models.PROTECT, default=1)
    timeToFinish = models.TimeField()
    isActive = models.BooleanField(default=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    def save(self, *args, **kwargs):
        current_date = timezone.now().date()
        if self.startDate <= current_date <= self.endDate:
            self.isActive = True
        else:
            self.isActive = False
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
class questions(models.Model):
    id = models.AutoField(primary_key=True)
    surveyId = models.ForeignKey(survey, on_delete=models.CASCADE, default=None)
    question = models.CharField(max_length=1000)
    options = models.CharField(max_length=50000)

class response(models.Model):
    id = models.AutoField(primary_key=True)
    questionId = models.ForeignKey(questions, on_delete=models.CASCADE)
    userID = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    userResponse = models.CharField(max_length=500, null=False)
    surveyId = models.ForeignKey(survey, default=None, on_delete=models.CASCADE)


class surveyHistory(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    companyId = models.ForeignKey(Company, on_delete=models.CASCADE)
    surveyID = models.ForeignKey(survey, on_delete=models.CASCADE)
    rewardStatus = models.BooleanField(default=False)