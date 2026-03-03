from django.db import models
from cloudinary.models import CloudinaryField

class HeroSection(models.Model):
    sub_title = models.CharField(max_length=100, default="Est. 2012 • Fine Dining")
    main_title_white = models.CharField(max_length=100, default="Crafting")
    main_title_span = models.CharField(max_length=50, default="Moments")
    main_title_bottom = models.CharField(max_length=100, default="Beyond Taste")
    menu_button_text = models.CharField(max_length=50, default="View Our Menu")
    story_button_text = models.CharField(max_length=50, default="Our Story")
    background_image = CloudinaryField('background_image', folder='banner/',blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "1. Hero Section"

class RestaurantFeature(models.Model):
    icon_class = models.CharField(max_length=50, help_text="e.g., fas fa-leaf")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "2. Restaurant Features"


class AboutSection(models.Model):
    image = CloudinaryField('image', folder='about/')
    experience_years = models.CharField(max_length=10, default="12Y")
    legacy_tag = models.CharField(max_length=50, default="The Legacy")
    title = models.CharField(max_length=200, default="Every Flavor Tells A Royal Story")
    description = models.TextField()
    
    # নিচের ৩টি স্ট্যাটিক নাম্বার/কাউন্টার
    stat1_count = models.CharField(max_length=20, default="50+")
    stat1_label = models.CharField(max_length=50, default="Master Recipes")
    
    stat2_count = models.CharField(max_length=20, default="20+")
    stat2_label = models.CharField(max_length=50, default="Expert Chefs")
    
    stat3_count = models.CharField(max_length=20, default="100%")
    stat3_label = models.CharField(max_length=50, default="Satisfaction")

    class Meta:
        verbose_name_plural = "3. About Section"

    def __str__(self):
        return self.title


