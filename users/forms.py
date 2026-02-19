from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ProfileModel


class SignUpForm(UserCreationForm):
    """Custom sign-up form for the Skill Barter Zone project.

    Collects:
      - login name (Django's built-in ``username`` field)
      - full name
      - email
      - password
      - address
      - gender (M/F/T)
    """

    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    gender = forms.ChoiceField(
        choices=ProfileModel.GENDER_CHOICES,
        required=True,
    )

    class Meta:
        model = User
        # ``username`` here is used as the logical "login name"
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the labels clearer for the project terminology
        self.fields["username"].label = "Login name"
        self.fields["username"].help_text = None
        self.fields["email"].label = "Email"

        # Remove default help texts that look noisy in the UI
        for fieldname in ["password1", "password2"]:
            self.fields[fieldname].help_text = None

    def clean_email(self):
        """Ensure that the email is unique across all users."""
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    # def save(self, commit: bool = True):
    #     """Create the user and fill in the profile fields.

    #     - ``username`` is treated as "login name"
    #     - ``email`` and password are stored on ``User``
    #     - full name, address and gender are stored on ``ProfileModel``
    #     """
    #     user = super().save(commit=False)

    #     if commit:
    #         user.save()

    #         # Update or create the related profile with extra info
    #         profile, _ = ProfileModel.objects.get_or_create(user=user)
    #         profile.login_name = user.username
    #         profile.full_name = self.cleaned_data.get("full_name", "")
    #         profile.address = self.cleaned_data.get("address", "")
    #         profile.gender = self.cleaned_data.get("gender", "")
    #         profile.save()

    #     return user
    def save(self, commit: bool = True):
        user = super().save(commit=False)

        full_name = self.cleaned_data.get("full_name", "").strip()
        parts = full_name.split()

        if commit:
            user.save()

            # Assign first & last name correctly
            if len(parts) == 1:
                user.first_name = parts[0]
                user.last_name = ""
            else:
                user.first_name = parts[0]
                user.last_name = parts[-1]

            user.save()

            # Update profile
            profile, _ = ProfileModel.objects.get_or_create(user=user)
            profile.login_name = user.username
            profile.full_name = full_name
            profile.address = self.cleaned_data.get("address", "")
            profile.gender = self.cleaned_data.get("gender", "")
            profile.save()

        return user



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Login name"
        for fieldname in ["username", "email", "first_name", "last_name"]:
            self.fields[fieldname].help_text = None


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ProfileModel
        fields = ["image", "full_name", "address", "gender"]
