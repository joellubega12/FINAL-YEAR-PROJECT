from django import forms
from .models import *
from account.forms import FormSettings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------- VOTER FORM ----------------
class VoterForm(FormSettings):
    class Meta:
        model = Voter
        fields = ['phone']


# ---------------- POSITION FORM ----------------
class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ['name', 'max_vote']


# ---------------- CANDIDATE FORM ----------------
class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = ['fullname', 'bio', 'position', 'photo']


# ---------------- REGISTER FORM ----------------
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    #  Validate email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return email

    #  Validate password match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    #  Save user with hashed password
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # 🔐 HASH PASSWORD
        user.is_verified = False  # Ensure user starts unverified

        if commit:
            user.save()

        return user