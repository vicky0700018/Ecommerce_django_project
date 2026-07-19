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
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
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
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
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

    @property
    def discount_percentage(self):
        if self.discount_price and self.price:
            try:
                discount = ((self.price - self.discount_price) / self.price) * 100
                return int(discount)
            except ZeroDivisionError:
                return 0
        return 0

    @property
    def approved_feedbacks(self):
        return self.feedbacks.filter(is_approved=True)

    @property
    def average_rating(self):
        approved = self.approved_feedbacks
        if not approved:
            return 0
        return round(sum(f.rating for f in approved) / len(approved), 1)

    @property
    def average_rating_stars(self):
        avg = self.average_rating
        return range(int(avg))



class Announcement(models.Model):
    text = models.CharField(max_length=255, help_text="Announcement text (e.g. Free Shipping All Over India)")
    link = models.URLField(blank=True, null=True, help_text="Optional link when the bar is clicked")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Designate if this announcement is displayed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.text


class TeamMember(models.Model):
    employee_image = models.ImageField(upload_to='team/', help_text="Upload employee photo")
    employee_name = models.CharField(max_length=150)
    role = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.employee_name} - {self.role}"


class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/', help_text="Upload gallery image")
    title = models.CharField(max_length=150, blank=True, help_text="Optional caption or title")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title or f"Gallery Image {self.id}"


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


class Order(models.Model):
    PAYMENT_METHODS = (
        ('COD', 'Cash On Delivery'),
        ('ONLINE', 'Online Payment'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.TextField(default="Order Items")

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id


class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    rating = models.IntegerField(default=5)  # 1 to 5 stars
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"{self.user.username}'s Cart - {self.product.name} ({self.quantity})"


class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"


class ContactPageConfiguration(models.Model):
    email = models.EmailField(default="support@shopsphere.com")
    phone = models.CharField(max_length=20, default="+91 1234567890")
    address = models.TextField(default="123 ShopSphere Street, India")
    working_hours = models.CharField(max_length=150, default="Mon - Sat: 9:00 AM - 6:00 PM")
    google_map_embed_url = models.TextField(blank=True, null=True, help_text="Google Maps Embed iframe URL or HTML")

    class Meta:
        verbose_name = 'Contact Page Configuration'
        verbose_name_plural = 'Contact Page Configuration'

    def __str__(self):
        return "Contact Page Configuration"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    warehouse_location = models.CharField(max_length=100, blank=True, null=True, default="Main Warehouse")
    last_restocked = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return f"Inventory for {self.product.name} (Stock: {self.product.stock})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Product)
def create_product_inventory(sender, instance, created, **kwargs):
    if created:
        Inventory.objects.get_or_create(product=instance)




