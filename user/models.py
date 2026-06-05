from django.db import models
from django.contrib.auth.models import User  # Import the default User model

# Model for additional user details
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the default User model
    phone = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.user.username

# Model for print orders
class PrintOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link directly to the default User model
    file = models.FileField()  # File uploaded to /media/orders/
    print_type = models.CharField(max_length=20, choices=[('black-white', 'Black & White'), ('color', 'Color')])
    paper_size = models.CharField(max_length=10, choices=[('A4', 'A4'), ('A3', 'A3'), ('Letter', 'Letter'), ('Legal', 'Legal')])
    copies = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[('COD', 'COD'), ('Paid', 'Paid')], default='COD')
    order_date = models.DateTimeField(auto_now_add=True)  # Auto store order timestamp
    order_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending')

    def __str__(self):
        return f"Order {self.id} - {self.file.name}"
