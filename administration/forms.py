from django import forms
from django.contrib.auth.models import Group, User
from basics.models import Groupdata, Userdata

class GroupFormRegister(forms.Form):
	class Meta:
		model = Groupdata
		fields = ['name','email']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if email and not User.objects.filter(email=email).count():
			raise forms.ValidationError(u'Email address must be from registered User')
		return email
		
