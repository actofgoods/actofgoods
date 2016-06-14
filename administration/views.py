from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from basics.models import Userdata, Groupdata, CategoriesNeeds, ContactUs, Need
from django.contrib.auth.models import User, Group
from administration.forms import GroupFormRegister
from basics.forms import CategoriesForm
from basics.views import getAddress
from basics.models import Address
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def categories(request):
	if request.user.is_authenticated():
		if request.method == 'POST':
			form = CategoriesForm(request.POST)
			if form.is_valid():
				name = request.POST.get('name')
				if not {'name':name} in CategoriesNeeds.objects.values('name'): 
					categorie = CategoriesNeeds.objects.create(name=name)
					categorie.save()
				else:
					messages.add_message(request, messages.INFO, 'categorie_exists')
	categories = CategoriesNeeds.objects.all()
	return render(request, 'administration/categories.html', {'categories':categories})

def categories_delete(request, pk):
	cat = ''
	if not CategoriesNeeds.objects.filter(name='sonstige'):
		cat = cat = CategoriesNeeds.objects.create(name='sonstige')
	else:
		cat = CategoriesNeeds.objects.get(name='sonstige')
	categorie = get_object_or_404(CategoriesNeeds, pk=pk)
	Need.objects.filter(categorie=categorie).update(categorie=cat)
	if not categorie.name == 'sonstige':
		categorie.delete()
	else:
		messages.add_message(request, messages.INFO, 'categorie_sonst')
	return redirect('administration:categories')
	#return render(request, 'administration/categories.html', {'categories':categories})

def groups(request):
	if request.user.is_authenticated():
		if request.method == "POST":
			form = GroupFormRegister(request.POST)
			if form.is_valid() :
				lat, lng = getAddress(request)
				email = request.POST.get('email')
				name = request.POST.get('name')
				if lat != None and lng != None:
					if {'email': email} in User.objects.values('email') and not Group.objects.filter(name='teeest'):
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
					elif not {'email': email} in User.objects.values('email') and not Group.objects.filter(name='teeest'):
						messages.add_message(request, messages.INFO, 'wrong_email')
					elif {'email': email} in User.objects.values('email') and Group.objects.filter(name='teeest'):
						messages.add_message(request, messages.INFO, 'wrong_group')
					else :
						messages.add_message(request, messages.INFO, 'wrong_emailAndGroup')

				else:
					messages.add_message(request, messages.INFO, 'location_failed')
			else:
				messages.add_message(request, messages.INFO, 'wrong_form')
	groups = Groupdata.objects.all()
	return render(request, 'administration/groups.html', {'groups': groups})

def informations(request):
	return render(request, 'administration/informations.html')

def requests(request):
    requests = ContactUs.objects.all().exclude(works_on=request.user)
    works_on = ContactUs.objects.filter(works_on=request.user)
    return render(request, 'administration/requests.html', {'requests': requests, 'works_on':works_on})

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
	#return render(request, 'administration/users.html', {'users':users})
	return redirect('administration:users')

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

#TODO: If we want to call this function from js we need a solution for csrf for test purposes i added csrf_exempt witch will ignore it
@csrf_exempt
def work_on_request(request):
	request_id = request.POST['id']
	contact = ContactUs.objects.get(id=request_id)
	contact.works_on = request.user
	contact.save()
	return redirect('administration:groups')
