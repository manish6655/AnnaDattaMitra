from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=False)
    state = models.CharField(max_length=50, default="")
    district = models.CharField(max_length=50, default="")
    city = models.CharField(max_length=50, default="")
    interests = models.TextField()

    def __str__(self):
        return self.name
    
# models.py

from django.db import models

class Product(models.Model):
    # Define quality choices as a tuple of (value, display_name)
    QUALITY_CHOICES = [
        ('poor', 'Poor'),
        ('good', 'Good'),
        ('best', 'Best'),
    ]

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=10, choices=[('kg', 'Kilograms'), ('gm', 'Grams')], default='kg')  # Add default here
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)  # Add choices here
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='product/', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='messages')  # Fixed attribute reference
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.name}: {self.content[:20]}"