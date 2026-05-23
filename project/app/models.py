from django.db import models

# Create your models here.
class Cyclone(models.Model):
    COUNTRY_CHOICES = {
        ('USA', 'United States'),
        ('India', 'India'),
        ('UK', 'United Kingdom'),
        ('Australia', 'Australia'),
        ('Canada', 'Canada'),
        ('Japan', 'Japan'),
        ('Germany', 'Germany'),
        ('Philippines', 'Philippines'),
        ('Bangladesh', 'Bangladesh'),
        ('Other', 'Other')
    }
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=155)
    password = models.CharField(max_length=55)
    contact = models.IntegerField()
    address = models.TextField(max_length=255)
    country = models.CharField(choices=COUNTRY_CHOICES)

    def __str__(self):
        return self.name

