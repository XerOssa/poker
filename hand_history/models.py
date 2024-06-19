from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    stack = models.IntegerField(default=100)
    
    def __str__(self):
        return self.name
