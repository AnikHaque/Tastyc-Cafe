from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Food(models.Model):
    # ... আপনার আগের ফিল্ডগুলো থাকবে ...
    MOOD_CHOICES = [
        ('happy', 'Happy (Celebration)'),
        ('stressed', 'Stressed (Comfort Food)'),
        ('romantic', 'Romantic (Date Night)'),
        ('lazy', 'Lazy (Quick Bites)'),
    ]
    mood_tag = models.CharField(max_length=20, choices=MOOD_CHOICES, default='happy')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = CloudinaryField('image', folder='foods/')
    is_available = models.BooleanField(default=True)
    is_today_special = models.BooleanField(default=False)
    
    # --- নতুন রিয়েলিস্টিক ফিচার ফিল্ডস ---
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10) # এর নিচে নামলে "Selling Fast" দেখাবে
    off_peak_discount = models.PositiveIntegerField(default=0) # শতাংশ (যেমন: ২০ মানে ২০%)
    # ----------------------------------

    # ... পুষ্টিগুণ ফিল্ডগুলো ...
    calories = models.IntegerField(default=0)
    protein = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    carbs = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    fats = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    ai_tags = models.CharField(max_length=255, blank=True, null=True)
    is_surprise_item = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # models.py এর Food ক্লাসের ভেতরে এটি যোগ করুন
    def get_meta_description(self):
        """অটোমেটিক এসইও মেটা ডেসক্রিপশন জেনারেট করবে"""
        mood_msg = f"Perfect for your {self.mood_tag} mood!" if self.mood_tag else ""
        cal_msg = f"Only {self.calories} calories." if self.calories > 0 else ""
        return f"Order {self.name} at RoyalDine. {self.description[:100]}. {mood_msg} {cal_msg} Authentic taste delivered to your door."

    # models.py এর Food ক্লাসের ভেতর
    def auto_manage_availability(self):
        """
        যদি স্টক ০ হয় অথবা খাবারটি আজকের স্পেশাল না হয়ে থাকে এবং 
        গত ৩ দিনে একবারও অর্ডার না হয়, তবে এটি অটোমেটিক 'is_available=False' করে দেবে।
        """
        if self.stock <= 0:
            self.is_available = False
            self.save()
            return False
        return self.is_available
    
    @property
    def get_dynamic_price(self):
        from datetime import datetime
        now_hour = datetime.now().hour
        current_price = self.price

        # লজিক ১: High Demand Surge (স্টক যখন বিপৎসীমার নিচে)
        # যদি স্টক ৩-এর নিচে নেমে যায়, তবে দাম ৫% বাড়িয়ে দাও (ডিমান্ড বেশি)
        if 0 < self.stock <= 3:
            current_price = self.price * 1.05 

        # লজিক ২: Happy Hour (দুপুর ৩টা - ৫টা)
        elif 15 <= now_hour < 17 and self.off_peak_discount > 0:
            discount = (self.price * self.off_peak_discount) / 100
            current_price = self.price - discount

        # লজিক ৩: Overstock Clearance (স্টক যখন অনেক বেশি, যেমন ১০০-এর উপরে)
        # স্টক ক্লিয়ার করার জন্য অটো ২% ছাড়
        elif self.stock > 100:
            current_price = self.price * 0.98

        return current_price

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        """চেক করবে স্টক কি বিপৎসীমার নিচে?"""
        return 0 < self.stock <= self.low_stock_threshold

    @property
    def get_dynamic_price(self):
        """সময় অনুযায়ী অটোমেটিক অফ-পিক ডিসকাউন্ট হিসাব করবে"""
        from datetime import datetime
        now_hour = datetime.now().hour
        
        # উদাহরণ: দুপুর ৩টা থেকে বিকাল ৫টা (১৫:০০ - ১৭:০০) অফ-পিক আওয়ার
        if 15 <= now_hour < 17 and self.off_peak_discount > 0:
            discount = (self.price * self.off_peak_discount) / 100
            return self.price - discount
        return self.price
    

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

    @property
    def discounted_price(self):
        if not self.food:
            return 0

        if not self.discount_percentage:
            return self.food.price

        discount = (self.food.price * self.discount_percentage) / 100
        return self.food.price - discount

    @property
    def is_valid(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date


class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.IntegerField()
    image = CloudinaryField('image', folder='testimonials/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}'s review"
    

class ComboDeal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', folder='combos/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class FlashDeal(models.Model):
    title = models.CharField(max_length=200, default='The "Gemini" Mega Combo')
    description = models.TextField()
    discount_text = models.CharField(max_length=50, default='40% OFF')
    image = CloudinaryField('image', folder='deals/')
    end_time = models.DateTimeField() 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def time_remaining(self):
        return self.end_time > timezone.now()