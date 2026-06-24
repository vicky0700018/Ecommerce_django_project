from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField()
    alternate_mobile_no = models.CharField(max_length=15, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - OTP"

    @staticmethod
    def generate_otp(user):
        """Generate and save OTP for user"""
        import random
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        
        # Delete any existing OTP for this user
        OTP.objects.filter(user=user).delete()
        
        # Create new OTP
        otp = OTP.objects.create(
            user=user,
            code=otp_code,
            expires_at=expires_at
        )
        return otp

    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at

    def verify(self, code):
        """Verify OTP code"""
        if self.is_expired():
            return False
        if self.code == code:
            self.is_verified = True
            self.save()
            return True
        return False


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, help_text="Unique slug for the category URL")
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class (e.g., 'fas fa-laptop')")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True, db_index=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price


class Announcement(models.Model):
    text = models.CharField(max_length=255, help_text="Announcement text (e.g. Free Shipping All Over India)")
    link = models.URLField(blank=True, null=True, help_text="Optional link when the bar is clicked")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Designate if this announcement is displayed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.text



