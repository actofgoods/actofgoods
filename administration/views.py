from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from basics.models import Userdata, Groupdata, CategoriesNeeds, ContactUs, Need, Information, Comment
from django.contrib.auth.models import User, Group
from administration.forms import GroupFormRegister, SearchUserForm
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
                if 'create_category' in form.data:
                    name = request.POST.get('name')
                    if not {'name':name} in CategoriesNeeds.objects.values('name'):
                        categorie = CategoriesNeeds.objects.create(name=name)
                        categorie.save()
                    else:
                        messages.add_message(request, messages.INFO, 'categorie_exists')
                elif 'search_category' in form.data:
                    name = request.POST.get('name')
                    if {'name':name} in CategoriesNeeds.objects.values('name'):
                        categ = CategoriesNeeds.objects.get(name=name)
                        return render(request, 'administration/categories.html', {'categ':categ})
                    else:
                        messages.add_message(request, messages.INFO, 'category_not_exists')
    categories = CategoriesNeeds.objects.all().order_by('name')
    return render(request, 'administration/categories.html', {'categories':categories})

def categories_delete(request, pk):
    cat = ''
    if not CategoriesNeeds.objects.filter(name='Other'):
        cat = CategoriesNeeds.objects.create(name='Other')
    else:
        cat = CategoriesNeeds.objects.get(name='Other')
    categorie = get_object_or_404(CategoriesNeeds, pk=pk)
    Need.objects.filter(categorie=categorie).update(categorie=cat)

    cat_users = Userdata.objects.filter(inform_about=cat)
    for u in cat_users:
        u.inform_about.remove(categorie)

    if not categorie.name == 'Other':
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
                if 'create_group' in form.data:
                    email = request.POST.get('email')
                    name = request.POST.get('name')
                    if {'email': email} in User.objects.values('email') and not Group.objects.filter(name=name):
                        #address = Address.objects.create(latitude=0.0, longditude=0.0)
                        data = form.cleaned_data
                        group = Group.objects.create(name=name)
                        user = User.objects.get(email=email)
                        user.is_staff = True
                        user.save()
                        group.user_set.add(user)
                        gdata = Groupdata(group=group)
                        gdata.save()
                        return redirect('administration:groups')
                    elif not {'email': email} in User.objects.values('email') and not Group.objects.filter(name=name):
                        messages.add_message(request, messages.INFO, 'wrong_email')
                    elif {'email': email} in User.objects.values('email') and Group.objects.filter(name=name):
                        messages.add_message(request, messages.INFO, 'wrong_group')
                    else :
                        messages.add_message(request, messages.INFO, 'wrong_emailAndGroup')
                elif 'search_group' in form.data:
                    name = request.POST.get('name')
                    if {'name':name} in Group.objects.values('name'):
                        gro = Group.objects.get(name=name)
                        return render(request, 'administration/groups.html', {'gro':gro})
                    else:
                        messages.add_message(request, messages.INFO, 'group_not_exists')
            else:
                messages.add_message(request, messages.INFO, 'wrong_form')
    groups = Groupdata.objects.all().order_by('group__name')
    return render(request, 'administration/groups.html', {'groups': groups})

@csrf_exempt
def informations(request):
    infos = Information.objects.all()
    if request.GET.__contains__('sel'):
        selected = request.GET['sel']
        if selected == 'all':
            infos = Information.objects.all().order_by('date')
        elif selected == 'reported informations':
            infos = Information.objects.filter(was_reported=True)
        elif selected == 'reported comments':
            comments = Comment.objects.filter(was_reported=True)
            return render(request, 'administration/informations.html', {'comments':comments})

    return render(request, 'administration/informations.html', {'infos':infos})

def information_admin(request, pk):
    information = get_object_or_404(Information, pk=pk)
    comments = Comment.objects.filter(inf=information).order_by('-date')
    return render(request, 'administration/information_admin.html', {'information':information, 'comments':comments})

def requests(request):
    requests = ContactUs.objects.all().exclude(works_on=request.user).order_by('create_date')
    works_on = ContactUs.objects.filter(works_on=request.user).order_by('create_date')
    return render(request, 'administration/requests.html', {'requests': requests, 'works_on':works_on})

@csrf_exempt
def needs(request):
    categories = CategoriesNeeds.objects.all().order_by('name')
    needs = Need.objects.all().order_by('date').reverse()
    if request.GET.__contains__('needs'):
        selected_need = request.GET['needs']
        selected_categorie = request.GET['categories']
        if selected_need == 'all':
            if selected_categorie == 'all':
                needs = Need.objects.all().order_by('date').reverse()
            else:
                categorie = CategoriesNeeds.objects.get(name=selected_categorie)
                needs = Need.objects.filter(categorie=categorie).order_by('date').reverse()
        elif selected_need == 'reported':
            if selected_categorie == 'all':
                needs = Need.objects.filter(was_reported=True).order_by('date').reverse()
            else:
                categorie = CategoriesNeeds.objects.get(name=selected_categorie)
                needs = Need.objects.filter(was_reported=True, categorie=categorie).order_by('date').reverse()

    return render(request, 'administration/needs.html', {'needs':needs,'categories':categories})

def users(request):
    users = sorted(get_list_or_404(User), key=lambda User: User.email)
    if request.user.is_authenticated():
        if request.method == "POST":
            form = SearchUserForm(request.POST)
            if form.is_valid():
                email = request.POST.get('email')
                if {'email': email} in User.objects.values('email'):
                    usr = User.objects.get(email=email)
                    if not usr.is_superuser:
                        return render(request, 'administration/users.html', {'usr':usr})
                    else:
                        messages.add_message(request, messages.INFO, 'user_isAdmin')
                else:
                    messages.add_message(request, messages.INFO, 'wrong_email')
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

@csrf_exempt
def information_delete(request):
    request_id = request.POST['id']
    info = get_object_or_404(Information, pk=request_id)
    info.delete()
    return redirect('administration:informations')

def info_delete(request, pk):
    info = get_object_or_404(Information, pk=pk)
    info.delete()
    return redirect('administration:informations')


@csrf_exempt
def need_delete(request):
    request_id = request.POST['id']
    need = get_object_or_404(Need, pk=request_id)
    need.delete()
    return redirect('administration:needs')

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

@csrf_exempt
def request_done(request):
    request_id = request.POST['id']
    request = get_object_or_404(ContactUs, pk=request_id)
    request.delete()
    return redirect('administration:requests')

@csrf_exempt
def comment_delete(request):
    comment = get_object_or_404(Comment, pk = request.POST['id'])
    comment.delete()
    return redirect('administration:needs')
