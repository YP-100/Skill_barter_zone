from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Skill(models.Model):
    """
    A skill that belongs to a specific user.

    Each skill is attached to the profile/user who offers it so that
    different users have different sets of skills.
    """

    user = models.ForeignKey(
        User,
        related_name="skills",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Barter(models.Model):
    # STATUS_PENDING = "Pending"
    # STATUS_ACCEPTED = "Accepted"
    # STATUS_REJECTED = "Rejected"
    # STATUS_COMPLETED = "Completed"

    # STATUS_CHOICES = [
    #     (STATUS_PENDING, "Pending"),
    #     (STATUS_ACCEPTED, "Accepted"),
    #     (STATUS_REJECTED, "Rejected"),
    #     (STATUS_COMPLETED, "Completed"),
    # ]
    STATUS_PENDING = "Pending"
    STATUS_ADMIN_APPROVED = "Admin Approved"
    STATUS_ACCEPTED = "Accepted"
    STATUS_REJECTED = "Rejected"
    STATUS_COMPLETED = "Completed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ADMIN_APPROVED, "Admin Approved"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    date_requested = models.DateTimeField(auto_now_add=True)
    date_responded = models.DateTimeField(blank=True, null=True)

    skill_from = models.ForeignKey(
        Skill,
        related_name="barters_from",
        on_delete=models.CASCADE,
    )
    skill_to = models.ForeignKey(
        Skill,
        related_name="barters_to",
        on_delete=models.CASCADE,
    )
    user_from = models.ForeignKey(
        User,
        related_name="barters_sent",
        on_delete=models.CASCADE,
    )
    user_to = models.ForeignKey(
        User,
        related_name="barters_received",
        on_delete=models.CASCADE,
    )
    admin = models.ForeignKey(
        User,
        related_name="barters_managed",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Admin user who manages this barter (optional).",
    )
    completed_by_from = models.BooleanField(default=False)
    completed_by_to = models.BooleanField(default=False)  

    def __str__(self) -> str:
        return f"Barter #{self.pk} - {self.user_from} -> {self.user_to}"


class Feedback(models.Model):
    barter = models.ForeignKey(Barter, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('barter', 'user')  # ensures each user gives only one feedback


    def __str__(self) -> str:
        return f"Feedback #{self.pk} for Barter #{self.barter_id}"


class Message(models.Model):
    """
    Very simple private message between two users.
    """

    sender = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.CASCADE,
    )
    recipient = models.ForeignKey(
        User,
        related_name="received_messages",
        on_delete=models.CASCADE,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Message from {self.sender} to {self.recipient} at {self.created_at}"
