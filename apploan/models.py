from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()  # Normalize email before saving
        super().save(*args, **kwargs)

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

# Define a function to generate a unique loan_id
def generate_loan_id():
    last_loan = Loan.objects.order_by('-id').first()  # Get the last loan entry
    if last_loan and last_loan.loan_id.startswith("LOAN"):
        last_number = int(last_loan.loan_id[4:])  # Extract the number part
        new_number = last_number + 1
    else:
        new_number = 1  # Start from LOAN001 if no previous loan exists
    return f"LOAN{new_number:03d}"  # Format as LOAN001, LOAN002, etc.  # Shortened UUID

class Loan(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]
    loan_id = models.CharField(
        max_length=20, 
        unique=True, 
        default=generate_loan_id,  # Use a function instead of lambda
        editable=False
    )
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="loans", null=True, blank=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def borrower_name(self, obj):
     """Display the borrower's email if username is not available"""
     return obj.borrower.username if obj.borrower.username else obj.borrower.email
    
class PaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, related_name='payment_schedule', on_delete=models.CASCADE)
    installment_no = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)