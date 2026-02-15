from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

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


from django.db import models
from django.utils import timezone


class Offer(models.Model):
    food = models.ForeignKey(
        'Food',
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

    def __str__(self):
        if self.food:
            return f"{self.title} - {self.food.name}"
        return self.title

    # ⭐ Discounted Price Safe
    @property
    def discounted_price(self):
        if not self.food:
            return 0

        if not self.discount_percentage:
            return self.food.price

        discount = (self.food.price * self.discount_percentage) / 100
        return self.food.price - discount

    # ⭐ Offer Valid Check
    @property
    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date


class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # আপনার বাকি ফিল্ডগুলো এখানে থাকবে...
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.IntegerField()
    image = models.ImageField(upload_to='testimonials/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}'s review"
    

class ComboDeal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='combos/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name