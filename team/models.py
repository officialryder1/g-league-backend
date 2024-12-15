from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
import os
import random
import string
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid

def generate_random_filename():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))

class User(AbstractUser):
    ROLE_CHOICES = (
        ('normal', 'Normal User'),
        ('player', 'Player'),
        ('coach', 'Coach')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team')
    abbr = models.CharField(max_length=5)
    bio = models.CharField(max_length=250)
    num_roaster = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    PLAYER_ROLE = {
        ('slayer', 'SLAYER'),
        ('objective', 'OBJECTIVE'),
        ('supporter', 'SUPPORTER'),
        ('anchor', 'ANCHOR')
    }
    name = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='players')
    role = models.CharField(max_length=9, choices=PLAYER_ROLE, default='objective')
    image = models.ImageField(upload_to='player_img')
    bio = models.CharField(max_length=150, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        if self.image:
            
            random_name = generate_random_filename() + os.path.splitext(self.image.name)[1]
            self.image.name = random_name

            image = Image.open(self.image)

            max_width = 500
            if image.width > max_width:
                ratio = max_width / float(image.width)
                new_height = int((float(image.height) * float(ratio)))
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)


            image_io = BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)

            self.image = InMemoryUploadedFile(
                image_io,
                'image',
                self.image.name,
                'image/jpeg',
                image_io.tell(),
                None
            )
        super(Player, self).save(*args, *kwargs)

class Coach(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='coach_img', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    bio = models.CharField(max_length=150, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
    
class Invitation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invitaions")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)