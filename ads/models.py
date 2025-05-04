from io import BytesIO
import os
from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

class Ad(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('other', 'Other'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used_good', 'Used - Good'),
        ('used_fair', 'Used - Fair'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        if self.image:
            image_path = self.image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        try:
            old_ad = Ad.objects.get(pk=self.pk)
            if old_ad.image and old_ad.image != self.image:
                old_image_path = old_ad.image.path
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
        except Ad.DoesNotExist:
            pass
        if self.image:
            img = Image.open(self.image)
            img = img.convert('RGB')
            max_size = (800, 800)
            img.thumbnail(max_size)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=70)
            buffer.seek(0)
            file_name = os.path.basename(self.image.name)
            self.image.save(file_name, ContentFile(buffer.read()), save=False)
        super().save(*args, **kwargs)

class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    ad_sender = models.ForeignKey('Ad', related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey('Ad', related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal: {self.ad_sender.title} → {self.ad_receiver.title} ({self.status})"
