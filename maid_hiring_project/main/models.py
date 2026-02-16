from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('maid', 'Maid'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

class MaidProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    SKILL_CHOICES = [
        ('cleaning', 'Cleaning'),
        ('cooking', 'Cooking'),
        ('babysitting', 'Babysitting'),
        ('elder_care', 'Elder Care'),
        ('laundry', 'Laundry'),
        ('other', 'Other Household Work'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='maid_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2)
    skills = models.CharField(max_length=255)
    aadhaar_document = models.FileField(upload_to='documents/aadhaar/')
    police_verification = models.FileField(upload_to='documents/police/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    maid = models.ForeignKey(MaidProfile, on_delete=models.CASCADE, related_name='bookings')
    service_date = models.DateField(help_text="When is the service required?", null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking: {self.customer.username} -> {self.maid.name} ({self.status})"
