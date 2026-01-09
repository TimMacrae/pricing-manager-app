from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

# Create your models here.


class User(AbstractUser):
    pass


class Product(models.Model):
    id: int = models.AutoField(primary_key=True)
    name: str = models.CharField(max_length=255)
    price: float = models.DecimalField(max_digits=10, decimal_places=2)
    stock_count: int = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="price_gt_zero"
            ),
            models.CheckConstraint(
                condition=models.Q(stock_count__gt=0),
                name="stock_count_gt_zero"
            ),
        ]

    def get_discounted_price(self, discount_percentage: float) -> float:
        return float(self.price) * (1 - discount_percentage / 100)

    @property
    def in_stock(self) -> bool:
        return self.stock_count > 0

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.stock_count < 0:
            raise ValidationError("Stock count cannot be negative.")
