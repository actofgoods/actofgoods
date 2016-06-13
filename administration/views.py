from django.shortcuts import render, get_object_or_404, redirect
from basics.models import Userdata, Groupdata, ContactUs
from django.contrib.auth.models import User, Group
from administration.forms import GroupFormRegister
from basics.views import getAddress
from basics.models import Address


# Create your views here.

def categories(request):
	return render(request, 'administration/categories.html')

def groups(request):
	groups = Groupdata.objects.all()
	return render(request, 'administration/groups.html', {'groups': groups})

def informations(request):
	return render(request, 'administration/informations.html')

def requests(request):
    requests = ContactUs.objects.all()
    return render(request, 'administration/requests.html', {'requests': requests})

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
			print('request')
			if form.is_valid() :
				print('formvalid')
				lat, lng = getAddress(request)
				if lat != None and lng != None:
					address = Address.objects.create(latitude=lat, longditude=lng)
					#data = cleaned_data <- this doesnt work?
					email = request.POST.get('email')
					phone = request.POST.get('phone')
					name = request.POST.get('name')
					group = Group.objects.create(name=name)
					gdata = Groupdata(group=group, email=email, phone=phone, address=address)
					gdata.save()
					return redirect('administration:groups')
	return render(request, 'administration/new_group.html')

def group_delete(request, pk):
	groupDa = get_object_or_404(Groupdata, pk=pk)
	group = groupDa.group
	group.delete()
	return redirect('administration:groups')

def group_addUser(request, pk):

	pass
