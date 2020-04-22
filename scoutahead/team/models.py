from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    POSITIONS = [
        ('TOP', 'Top'),
        ('JUN', 'Jungle'),
        ('MID', 'Mid'),
        ('BOT', 'Bot'),
        ('SUP', 'Support'),
    ]
    position = models.CharField(max_length=3, choices=POSITIONS)
    phone = PhoneNumberField()
    email = models.EmailField(max_length=254)
    handle = models.CharField(max_length=50)
    time_zone = models.CharField(max_length=5)
    discord = models.CharField(max_length=50)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, blank=True, null=True)

class Team(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='static/')
    players = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='players')

class Game(models.Model):
    date = models.DateTimeField('Game Date')
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    champion = models.CharField(max_length=20)
    won = models.BooleanField()
    kill = models.IntegerField()
    death = models.IntegerField()
    assist = models.IntegerField()
    creep_score = models.IntegerField()
    vision_score = models.IntegerField()
    ward_placed = models.IntegerField()
    ward_destroyed = models.IntegerField()
    control_ward = models.IntegerField()