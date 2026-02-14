from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Food(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='foods/')
    is_available = models.BooleanField(default=True)
    is_today_special = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Offer(models.Model):
    food = models.ForeignKey(
    Food,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    # ⭐ Calculated property
    @property
    def discounted_price(self):
        if not self.food or not self.discount_percent:
            return self.food.price if self.food else 0

        discount = (self.food.price * self.discount_percent) / 100
        return self.food.price - discount

