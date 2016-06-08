from django import forms
from django.contrib.auth.models import User
from .models import Need, Information, Userdata
from nocaptcha_recaptcha.fields import NoReCaptchaField


class UserFormRegister(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password','email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email

class NeedFormNew(forms.ModelForm):
	class Meta:
		model = Need
		fields = ['headline','text','categorie']

class InformationFormNew(forms.ModelForm):
	class Meta:
		model = Information
		fields = ['headline','text']

class CaptchaForm(forms.Form):
    captcha = NoReCaptchaField()

class ProfileForm(forms.Form):
	class Meta:
		model = Userdata
		fields= ['pseudonym','phone']

class ProfileUserForm(forms.Form):
    class Meta:
        model = User
        fields = ['last_login', 'date_joined']

class ImmediateAidFormNew(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email

class PasswordForm(forms.Form):
	oldpw = forms.CharField(label='oldpw', max_length=100)
	newpw1 = forms.CharField(label='newpw1', max_length=100)
	newpw2 = forms.CharField(label='newpw2', max_length=100)
