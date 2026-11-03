from django.db import models
from django.conf import settings
CATEGORIES=['Network','Maintenance','Classroom','Administration']
STATUSES=['Open','In progress','Resolved']
class Ticket(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title=models.CharField(max_length=160)
    category=models.CharField(max_length=40)
    location=models.CharField(max_length=160)
    description=models.TextField()
    status=models.CharField(max_length=30,default='Open')
    priority=models.CharField(max_length=20,default='Normal')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
class Update(models.Model):
    ticket=models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='updates')
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
class Message(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    role=models.CharField(max_length=20)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
class FAQ(models.Model):
    title=models.CharField(max_length=160)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
