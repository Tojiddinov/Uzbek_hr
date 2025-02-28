from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, JobApplication
from .models import Resume
from .models import Job
from .models import TestAnswer
from django.contrib.auth import get_user_model


# === Custom User Registration Form === #
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="Role", widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}))
    employer_type = forms.ChoiceField(choices=CustomUser.EMPLOYER_TYPE_CHOICES, required=False, label="Employer Type", widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'employer_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Confirm Password'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        employer_type = cleaned_data.get("employer_type")

        if role == 'employer' and not employer_type:
            self.add_error('employer_type', "Employers must select either Company or University.")

        return cleaned_data


# === Job Application Form === #
class JobApplicationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Last Name'}))
    university_status = forms.ChoiceField(choices=[('studying', 'Currently Studying'), ('graduated', 'Graduated')], required=True, widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}))
    university_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'University Name'}))
    study_years = forms.CharField(max_length=9, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'e.g., 2021-2025'}))
    faculty = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Faculty'}))
    graduation_year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Graduation Year'}))
    age = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Age'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Email'}))
    username = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Username'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'Phone Number'}))
    resume = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}))
    cover_letter = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}))
    linkedin_profile = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'w-full p-2 border rounded-lg', 'placeholder': 'LinkedIn Profile (Optional)'}))

    class Meta:
        model = JobApplication
        fields = [
            'first_name', 'last_name', 'university_status', 'university_name',
            'study_years', 'faculty', 'graduation_year', 'email', 'username',
            'phone_number', 'resume', 'cover_letter', 'linkedin_profile'
        ]




class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "company", "location", "category", "description", "requirements", "salary", "employment_type"]
class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["full_name", "email", "phone", "linkedin", "resume_file"]



class AnswerForm(forms.ModelForm):
    class Meta:
        model = TestAnswer
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


User = get_user_model()  # CustomUser modelini olish

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="job_seeker_profile")
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    university_name = models.CharField(max_length=200, null=True, blank=True)
    faculty = models.CharField(max_length=200, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Job Seeker Profile"


