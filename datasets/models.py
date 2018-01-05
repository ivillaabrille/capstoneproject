from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class DataSet(models.Model):
    STATUS_CHOICES = (
        ('Approved', 'Approved'),
        ('Not yet Approved', 'Not yet Approved'),
    )

    DataSet_Title = models.CharField(max_length=100)
    DataSet_Description = models.TextField()
    DataSet_Poster = models.ForeignKey(User)
    DataSet_Posted = models.DateTimeField(default=datetime.now)
    DataSet_Status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Not yet Approved')
    Data = models.TextField(blank=True)
    jsonifiedData_url = models.CharField(max_length=100, blank=True)
    csvfiedData_url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.DataSet_Title
