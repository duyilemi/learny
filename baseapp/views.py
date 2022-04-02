from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import HttpResponse


# from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, CreateUserForm

# Create your views here.

# rooms = [
#     {"id": 1, "name": "I love Beau"},
#     {"id": 2, "name": "I love Luna"},
#     {"id": 3, "name": "I love Chanel"},
# ]

def LoginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password does not exist")

    context = {"page": page}
    return render(request, 'base/register_login.html', context)

def RegisterUser(request):

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Registration error")


    context = {"form": form}
    return render(request, 'base/register_login.html', context)

def LogoutUser(request):
    logout(request)
    return redirect('home')
    
def home(request):
    # getting query value from request
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # getting room  associated with query value... "__"enables topic to access name inside its parent...
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    room_count = rooms.count()

    topics = Topic.objects.all()[0 : 4]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) 
    context = {"rooms": rooms, "topics": topics, "room_count": room_count, "room_messages": room_messages}
    return render(request, 'base/home.html', context)


def userProfile(request, params):
    user = User.objects.get(id=params)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context= {"user": user, "rooms": rooms, "room_messages": room_messages, "topics": topics}
    return render(request, 'base/user_profile.html', context)


def room(request, params):
    # room = None
    # for item in rooms:
    #     if item["id"] == int(params):
    #         room = item
    room = Room.objects.get(id = params)
    # getting all related messages from Room child model ... Messages(as messages)..many to one uses "set.all()"...
    room_messages = room.message_set.all()
    # many to many relationship can use "all()"
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        # adding user that joins the conversation as one of the participants
        room.participants.add(request.user)
        return redirect("room", params= room.id)

    context = {"room": room, "room_messages": room_messages, "participants": participants}
    return render(request, "base/room.html", context)



# decorator to resist not logged users to create room
@login_required(login_url= 'login')
def createRoom(request):
    topics = Topic.objects.all()
    form = RoomForm()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        # a method that creates new topic if it has not been created already

        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )

        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     # creating and instance of particular room ...add()
        #     # form.save()
        #     room = form.save(commit=False)
        #     # adding the user as the host ...
        #     room.host = request.user
        #     room.save()
        
        return redirect('home')
    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)

@login_required(login_url= 'login')
def updateRoom(request, params):
    topics = Topic.objects.all()
    # getting room whose id match the request
    room = Room.objects.get(id=params)
    # pre-filling the form ... 
    form = RoomForm(instance=room)

# stop a user from updating other users room
    if request.user != room.host:
        return HttpResponse("You are not allowed to do this")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        # a method that creates new topic if it has not been created already
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {"form": form, "topics": topics, "room": room,}
    return render(request, 'base/room_form.html', context)

@login_required(login_url= 'login')
def deleteRoom(request,params):
    room = Room.objects.get(id = params)

# stop a user from deleting other users room
    if request.user != room.host:
        return HttpResponse("You are not allowed to do this")


    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {"obj":room})


@login_required(login_url= 'login')
def deleteMessage(request,params):
    message = Message.objects.get(id = params)

# stop a user from deleting other users room
    if request.user != message.user:
        return HttpResponse("You are not allowed to do this")


    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {"obj":message})


@login_required(login_url= 'login')
def updateUser(request):
    form = UserForm(instance=request.user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', params = request.user.id)

    
    return render(request, 'base/update_user.html', {"form": form,})


def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__contains=q)
    return render(request, 'base/topics.html', {"topics": topics})


def activities(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activities.html', {"room_messages": room_messages})