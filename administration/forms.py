from django import forms
from django.contrib.auth.models import Group, User
from basics.models import Groupdata, Userdata, ContactUs
from django.utils.translation import ugettext_lazy as _


class GroupFormRegister(forms.ModelForm):
	#name = forms.CharField(error_messages={'required': 'Please let us know what to call you!'})
    
	class Meta:
		model = Groupdata
		fields = ['name','email', 'is_GO']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if email and not User.objects.filter(email=email).count():
			raise forms.ValidationError(u'Email address must be from registered User')
		return email

class SearchUserForm(forms.Form):
	class Meta:
		model = Userdata
		fields = ['email']

class RequestForm(forms.Form):
    class Meta:
        model = ContactUs
        fields = ['key']
