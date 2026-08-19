from django import forms
from .models import PlatformSettings


class PlatformSettingsForm(forms.ModelForm):
    """Form for editing platform settings"""
    
    class Meta:
        model = PlatformSettings
        fields = [
            'site_name', 'site_description', 'site_logo', 'site_favicon',
            'contact_email', 'support_phone', 'support_email', 'company_address', 'business_hours',
            'default_delivery_fee', 'free_delivery_threshold', 'tax_rate',
            'allow_registration', 'allow_restaurant_registration', 'maintenance_mode',
            'facebook_url', 'twitter_url', 'instagram_url',
            'meta_title', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter platform name'
            }),
            'site_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter platform description'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact email'
            }),
            'support_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter support phone number'
            }),
            'support_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter support email'
            }),
            'company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter company address'
            }),
            'business_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mon-Sun: 9:00 AM - 10:00 PM'
            }),
            'default_delivery_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'free_delivery_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/yourpage'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/yourhandle'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/yourhandle'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO meta title (max 60 characters)',
                'maxlength': '60'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'SEO meta description (max 160 characters)',
                'maxlength': '160'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO keywords (comma separated)'
            }),
            'site_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'site_favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text and labels
        self.fields['site_name'].help_text = 'The name displayed on your platform'
        self.fields['site_description'].help_text = 'Brief description shown on homepage'
        self.fields['site_logo'].help_text = 'Upload your platform logo (recommended: 200x60px)'
        self.fields['site_favicon'].help_text = 'Upload your platform favicon (recommended: 32x32px)'
        self.fields['contact_email'].help_text = 'Main contact email for the platform'
        self.fields['support_phone'].help_text = 'Customer support phone number'
        self.fields['support_email'].help_text = 'Customer support email'
        self.fields['company_address'].help_text = 'Physical address of your company'
        self.fields['business_hours'].help_text = 'Platform operating hours'
        self.fields['default_delivery_fee'].help_text = 'Default delivery fee for orders'
        self.fields['free_delivery_threshold'].help_text = 'Minimum order amount for free delivery'
        self.fields['tax_rate'].help_text = 'Tax rate as percentage (e.g., 8.5 for 8.5%)'
        self.fields['allow_registration'].help_text = 'Allow new users to register'
        self.fields['allow_restaurant_registration'].help_text = 'Allow new restaurants to register'
        self.fields['maintenance_mode'].help_text = 'Enable maintenance mode (shows maintenance page)'
        self.fields['facebook_url'].help_text = 'Your Facebook page URL'
        self.fields['twitter_url'].help_text = 'Your Twitter profile URL'
        self.fields['instagram_url'].help_text = 'Your Instagram profile URL'
        self.fields['meta_title'].help_text = 'SEO title for search engines (max 60 characters)'
        self.fields['meta_description'].help_text = 'SEO description for search engines (max 160 characters)'
        self.fields['meta_keywords'].help_text = 'SEO keywords for search engines (comma separated)'
    
    def clean_meta_title(self):
        title = self.cleaned_data.get('meta_title')
        if title and len(title) > 60:
            raise forms.ValidationError('Meta title should be 60 characters or less.')
        return title
    
    def clean_meta_description(self):
        description = self.cleaned_data.get('meta_description')
        if description and len(description) > 160:
            raise forms.ValidationError('Meta description should be 160 characters or less.')
        return description
    
    def clean_tax_rate(self):
        tax_rate = self.cleaned_data.get('tax_rate')
        if tax_rate and (tax_rate < 0 or tax_rate > 100):
            raise forms.ValidationError('Tax rate must be between 0 and 100.')
        return tax_rate
