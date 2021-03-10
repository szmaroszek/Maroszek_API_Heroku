from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Car(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    avg_rating = models.FloatField(default=0)

class Rating(models.Model):
    car_id = models.ForeignKey(Car, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
