from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class ProfileModel(models.Model):
    """Extended profile information for each user.

    This stores additional fields needed for the Skill Barter Zone project
    such as full name, address and gender (M/F/T).
    """

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_TRANSGENDER = 'T'

    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_TRANSGENDER, 'Transgender'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Acts as the logical "login name" for the project
    login_name = models.CharField(max_length=150, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    image = models.ImageField(
        default='default.jpg',
        upload_to='profile',
        validators=[FileExtensionValidator(['png', 'jpg'])]
    )

    def __str__(self) -> str:
        return self.user.username
