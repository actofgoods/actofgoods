from django import forms
from django.contrib.auth.models import Group, User
from basics.models import Groupdata

class GroupFormRegister(forms.Form):
	class Meta:
		model = Groupdata
		fields = ['email','phone']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if email and User.objects.filter(email=email).count():
			raise forms.ValidationError(u'Email addresses must be unique.')
		return email
