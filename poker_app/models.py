from django.db import models

class Hero(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name


class GameConfig(models.Model):
    initial_stack = models.IntegerField()
    small_blind = models.IntegerField()
    ante = models.IntegerField()