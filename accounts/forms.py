from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'user_role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all visible fields
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            if 'form-control' not in css_class:
                field.widget.attrs['class'] = (css_class + ' form-control').strip()

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            if 'form-control' not in css_class:
                field.widget.attrs['class'] = (css_class + ' form-control').strip()

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get('class', '')
            if 'form-control' not in css_class:
                field.widget.attrs['class'] = (css_class + ' form-control').strip()
