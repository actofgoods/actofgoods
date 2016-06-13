from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from basics.models import Userdata, Groupdata, CategoriesNeeds
from django.contrib.auth.models import User, Group
from administration.forms import GroupFormRegister
from basics.forms import CategoriesForm
from basics.views import getAddress
from basics.models import Address
from django.contrib import messages

# Create your views here.

def categories(request):
	if request.user.is_authenticated():
		if request.method == 'POST':
			form = CategoriesForm(request.POST)
			if form.is_valid():
				name = request.POST.get('name')
				categorie = CategoriesNeeds.objects.create(name=name)
				categorie.save()
	categories = CategoriesNeeds.objects.all()
	return render(request, 'administration/categories.html', {'categories':categories})

def categories_delete(request, pk):
	categorie = get_object_or_404(CategoriesNeeds, pk=pk)
	categorie.delete()
	categories = CategoriesNeeds.objects.all()
	return render(request, 'administration/categories.html', {'categories':categories})

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
	users = get_list_or_404(User)
	return render(request, 'administration/users.html', {'users': users})

def user_delete(request, pk):
	# User somehow doesn't have attribute pk (only Userdata has), so we get the email from userdata and with that we get the user and can delete him
	user = get_object_or_404(User, pk=pk)
	user.delete()
	users = get_list_or_404(User)
	return render(request, 'administration/users.html', {'users':users})

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
						user.is_staff = True
						user.save()
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


def make_admin(request, pk):
	user = get_object_or_404(User, pk=pk)
	user.is_superuser = True
	user.save()
	users = get_list_or_404(User)
	return render(request, 'administration/users.html', {'users':users})
