from django.shortcuts import render


# Create your views here.

def categories(request):
	return render(request, 'administration/categories.html')

def groups(request):
	return render(request, 'administration/groups.html')

def informations(request):
	return render(request, 'administration/informations.html')

def mails(request):
	return render(request, 'administration/mails.html')

def needs(request):
	return render(request, 'administration/needs.html')

def users(request):
	return render(request, 'administration/users.html')