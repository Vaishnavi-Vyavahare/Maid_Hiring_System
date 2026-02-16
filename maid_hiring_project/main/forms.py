from django import forms
from .models import MaidProfile
from django.utils.translation import gettext_lazy as _

class MaidProfileForm(forms.ModelForm):
    SKILL_CHOICES = [
        ('cleaning', _('Cleaning')),
        ('cooking', _('Cooking')),
        ('babysitting', _('Babysitting')),
        ('elder_care', _('Elder Care')),
        ('laundry', _('Laundry')),
        ('other', _('Other Household Work')),
    ]
    
    skills = forms.MultipleChoiceField(
        choices=SKILL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_('Skills')
    )

    class Meta:
        model = MaidProfile
        fields = [
            'name', 'email', 'mobile_number', 'location', 
            'expected_salary', 'skills', 'aadhaar_document', 'police_verification'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your full name')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter mobile number'), 'type': 'tel'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Enter your location')}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Enter expected monthly salary')}),
            'aadhaar_document': forms.FileInput(attrs={'class': 'form-control'}),
            'police_verification': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Full Name'),
            'email': _('Email Address'),
            'mobile_number': _('Mobile Number'),
            'location': _('Location'),
            'expected_salary': _('Expected Salary'),
            'aadhaar_document': _('Aadhaar Document'),
            'police_verification': _('Police Verification'),
        }

    def clean_skills(self):
        # Convert list of skills to a comma-separated string for storage
        skills_list = self.cleaned_data.get('skills')
        if skills_list:
            return ", ".join(skills_list)
        return ""

class ContactMaidForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        }),
        label=_('Subject')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...'
        }),
        label=_('Message')
    )
