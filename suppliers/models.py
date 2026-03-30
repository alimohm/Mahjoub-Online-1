from django.db import models
from django.contrib.auth.models import User

class SupplierWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    verified = models.BooleanField(default=False)

    def __str__(self): return self.store_name
