from django import forms
from django.contrib.auth.models import User

class UserFormRegister(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password','email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email