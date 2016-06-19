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
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser not request.user.is_staff:
        return redirect('basics:home')
   
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
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
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
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
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
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    infos = Information.objects.all()
    selected = 'all'
    if request.GET.__contains__('sel'):
        selected = request.GET['sel']
        if selected == 'all':
            infos = Information.objects.all().order_by('date')
        elif selected == 'reported informations':
            infos = Information.objects.filter(was_reported=True)
        elif selected == 'reported comments':
            comments = Comment.objects.filter(was_reported=True)
            return render(request, 'administration/informations.html', {'comments':comments, 'current_info':selected})

    return render(request, 'administration/informations.html', {'infos':infos,'current_info':selected})

def information_admin(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    information = get_object_or_404(Information, pk=pk)
    comments = Comment.objects.filter(inf=information).order_by('date')
    return render(request, 'administration/information_admin.html', {'information':information, 'comments':comments})

def information_reported_comment_admin(request, pki, pkc):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    information = get_object_or_404(Information, pk=pki)
    comments = Comment.objects.filter(inf=information).order_by('date')
    reported_comment = comments.get(pk=pkc)
    return render(request, 'administration/information_admin.html', {'information':information, 'comments':comments, 'reported_comment':reported_comment})

def requests(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    requests = ContactUs.objects.all().filter(works_on=None).order_by('create_date')
    works_on = ContactUs.objects.filter(works_on=request.user).order_by('create_date')
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            if 'filter_in_progress_requests' in form.data:
                if {'email':email} in works_on.values('email'):
                    filter_in_progress = works_on.filter(email=email)
                    return render(request, 'administration/requests.html', {'requests': requests, 'filter_in_progress':filter_in_progress})
                else:
                    messages.add_message(request, messages.INFO, 'wrong_email_filter_in_progress')
            elif 'filter_new_requests' in form.data:
                if {'email':email} in requests.values('email'):
                    filter_new = requests.filter(email=email)
                    return render(request, 'administration/requests.html', {'works_on': works_on, 'filter_new':filter_new})
                else:
                    messages.add_message(request, messages.INFO, 'wrong_email_filter_new')
    return render(request, 'administration/requests.html', {'requests': requests, 'works_on':works_on})

@csrf_exempt
def needs(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    categories = CategoriesNeeds.objects.all().order_by('name')
    needs = Need.objects.all().order_by('date').reverse()
    selected_categorie = 'all Categories'
    selected_need = 'all'
    if request.GET.__contains__('needs'):
        selected_need = request.GET['needs']
        selected_categorie = request.GET['categories']
        if selected_need == 'all':
            if selected_categorie == 'all':
                needs = Need.objects.all().order_by('date').reverse()
                selected_categorie = 'all Categories'
            else:
                categorie = CategoriesNeeds.objects.get(name=selected_categorie)
                needs = Need.objects.filter(categorie=categorie).order_by('date').reverse()
                selected_categorie = categorie
        elif selected_need == 'reported':
            if selected_categorie == 'all':
                needs = Need.objects.filter(was_reported=True).order_by('date').reverse()
                selected_categorie = 'all Categories'
            else:
                categorie = CategoriesNeeds.objects.get(name=selected_categorie)
                needs = Need.objects.filter(was_reported=True, categorie=categorie).order_by('date').reverse()
                selected_categorie = categorie
    return render(request, 'administration/needs.html', {'needs':needs,'categories':categories,'current_cat':selected_categorie, 'current_need':selected_need})

def users(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    users = sorted(get_list_or_404(User), key=lambda User: User.email)
    if request.user.is_authenticated():
        if request.method == "POST":
            form = SearchUserForm(request.POST)
            if form.is_valid():
                email = request.POST.get('email')
                if {'email': email} in User.objects.values('email'):
                    usr = User.objects.get(email=email)
                else:
                    messages.add_message(request, messages.INFO, 'wrong_email')
    return render(request, 'administration/users.html', {'users': users})

def user_delete(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
	# User somehow doesn't have attribute pk (only Userdata has), so we get the email from userdata and with that we get the user and can delete him
    user = get_object_or_404(User, pk=pk)
    user.delete()
    users = get_list_or_404(User)
	#return render(request, 'administration/users.html', {'users':users})
    return redirect('administration:users')

def group_delete(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    groupDa = get_object_or_404(Groupdata, pk=pk)
    group = groupDa.group
    group.delete()
    return redirect('administration:groups')

@csrf_exempt
def information_delete(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    request_id = request.POST['id']
    info = get_object_or_404(Information, pk=request_id)
    info.delete()
    return redirect('administration:informations')

def info_delete(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    info = get_object_or_404(Information, pk=pk)
    info.delete()
    return redirect('administration:informations')


@csrf_exempt
def need_delete(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    request_id = request.POST['id']
    need = get_object_or_404(Need, pk=request_id)
    need.delete()
    return redirect('administration:needs')

def make_admin(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    user = get_object_or_404(User, pk=pk)
    user.is_staff = True
    #user.is_superuser = True
    user.save()
    users = get_list_or_404(User)
    return render(request, 'administration/users.html', {'users':users})

def admin_work_on_request(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    contact = ContactUs.objects.get(pk=pk)
    if contact.works_on == None:
        contact.works_on = request.user
        contact.save()
    else:
        messages.add_message(request, messages.INFO, 'other_admin_is_working_on_this_request')
    requests = ContactUs.objects.all().filter(works_on=None).order_by('create_date')
    works_on = ContactUs.objects.filter(works_on=request.user).order_by('create_date')
    return redirect('administration:requests')

@csrf_exempt
def request_done(request):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    request_id = request.POST['id']
    request = get_object_or_404(ContactUs, pk=request_id)
    request.delete()
    return redirect('administration:requests')

@csrf_exempt
def comment_delete(request, pk):
    if not request.user.is_authenticated():
        return redirect('basics:actofgoods_startpage')
    if not request.user.is_active:
        return render(request, 'basics/verification.html', {'active':False})
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('basics:home')
    comment = get_object_or_404(Comment, pk = pk)
    comment.delete()
    return redirect('administration:informations')
