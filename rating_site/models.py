from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    developer = models.CharField(max_length=100, blank=False)
    producer = models.CharField(max_length=100, blank=False)
    operating_system = models.CharField(max_length=100, blank=False)
    genre = models.CharField(max_length=100, blank=False)
    year = models.DateField(blank=False)
