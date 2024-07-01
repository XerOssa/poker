from django.db import models

class Hero(models.Model):
    name = models.CharField(max_length=100)
    stack = models.IntegerField(default=100)
    
    def __str__(self):
        return self.name


class GameConfig(models.Model):
    initial_stack = models.IntegerField(default=100)
    small_blind = models.IntegerField(default=1)
    ante = models.IntegerField(default=0)