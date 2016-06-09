from django.shortcuts import render, get_object_or_404, redirect
from basics.models import Userdata, Groupdata
from django.contrib.auth.models import User, Group
from administration.forms import GroupFormRegister
from basics.views import getAddress
from basics.models import Address
from django.contrib import messages

# Create your views here.

def categories(request):
	return render(request, 'administration/categories.html')

def groups(request):
	groups = Groupdata.objects.all()
	return render(request, 'administration/groups.html', {'groups': groups})

def informations(request):
	return render(request, 'administration/informations.html')

def mails(request):
	return render(request, 'administration/mails.html')

def needs(request):
	return render(request, 'administration/needs.html')

def users(request):
	users = Userdata.objects.order_by('pseudonym')
	return render(request, 'administration/users.html', {'users': users})

def user_delete(request, pk):
	# User somehow doesn't have attribute pk (only Userdata has), so we get the email from userdata and with that we get the user and can delete him
	userDa = get_object_or_404(Userdata, pk=pk)
	user = User.objects.get(username=userDa.user)
	user.delete()
	return redirect('administration:users')

def new_group(request):
	if request.user.is_authenticated():
		if request.method == "POST":
			form = GroupFormRegister(request.POST)
			if form.is_valid() :
				lat, lng = getAddress(request)
				email = request.POST.get('email')
				name = request.POST.get('name')
				if lat != None and lng != None:
					if {'email': email} in User.objects.values('email'):
						address = Address.objects.create(latitude=lat, longditude=lng)
						data = form.cleaned_data
						group = Group.objects.create(name=name)
						user = User.objects.get(email=email)
						group.user_set.add(user)
						gdata = Groupdata(group=group, address=address)
						gdata.save()
						return redirect('administration:groups')
					else:
						messages.add_message(request, messages.INFO, 'wrong_email')
				else:
					messages.add_message(request, messages.INFO, 'location_failed')
			else:
				messages.add_message(request, messages.INFO, 'wrong_form')
	return render(request, 'administration/new_group.html')

def group_delete(request, pk):
	groupDa = get_object_or_404(Groupdata, pk=pk)
	group = groupDa.group
	group.delete()
	return redirect('administration:groups')
