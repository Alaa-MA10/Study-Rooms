from http.client import HTTPResponse

from django.shortcuts import render, redirect
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm, CustomUserCreationForm


# Create your views here.

# ------------------------------ // User view\\ ------------------------------ #
def loginPage(request):

    page = 'login'

    # the User logged-in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password') 

        # Using the Django authentication system to verify a set of credentials.
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # A backend authenticated the credentials
            # attach authenticated user to the current session,
            # login() saves the user’s ID in the session, using Django’s session framework.
            login(request,user)
            return redirect('home')

        else:
            # No backend authenticated the credentials
            messages.error(request, 'Username OR Password not correct')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    # When logout() called, session data for the current request is completely cleaned out.
    logout(request)

    return redirect('home')


def registerPage(request):
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'An error occurred during registration')

    context = {'form':form}
    return render(request, 'base/login_register.html', context)


def userProfile(request, id):
    user = User.objects.get(pk=id)
    rooms = user.room_set.all()  # get all children of model(room)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)


#Restrict User, just logged-in user can update their data
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', id=user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html', context)

# ------------------------------ // End-User view\\ ------------------------------ #

# ------------------------------ // Home view\\ ------------------------------ #

def home(request):
    # filter home content(rooms, activities messages) based on search or selected topic
    query = request.GET.get('q') if request.GET.get('q') else ''

    rooms = Room.objects.filter( 
        Q(topic__name__icontains=query)| 
        Q(name__icontains=query) |
        Q(description__icontains=query)
        )

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    topics = Topic.objects.all()

    context = {'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)


def topicsPage(request):
    # filter content(rooms) based on search or selected topic
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics':topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    # get all room-messages
    room_messages = Message.objects.all()

    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html',context)

# ------------------------------ // End-Home view\\ ------------------------------ #


# ------------------------------ // Room view\\ ------------------------------ #
def room(request, id):
    room = Room.objects.get(pk=id)
    room_messages = room.message_set.all() # one-to-many relation, so, use _set (get all children of model(message))
    participants = room.participants.all() # many-to-many relation, so, use .all() direct

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', id=room.id)
    
    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)


#Restrict User, just logged-in user can create-room
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        # looking up for given topic_name, creating one if not exist 
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        room.save()
        # the user who creates the room, also one of the participants
        room.participants.add(request.user)

        return redirect('room', room.id)

    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


#Restrict User, just logged-in user can update-room
@login_required(login_url='login')
def updateRoom(request, id):
    room = Room.objects.get(pk=id)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    # Only Room-host allowed updating room data  
    if request.user != room.host:
        return HTTPResponse("Your not allowed here !!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')

        room.save()
        return redirect('room', room.id)

    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


#Restrict User, just logged-in user can delete-room
@login_required(login_url='login')
def deleteRoom(request, id):
    room = Room.objects.get(pk=id)

    # Only Room-host allowed deleting room  
    if request.user != room.host:
        return HTTPResponse("Your not allowed here !!")

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    context = {'obj':room}
    return render(request, 'base/delete.html', context)

# ------------------------------ // End-Room \\ ------------------------------ #

# ------------------------------ // Messages view\\ ------------------------------ #
#Restrict User, just logged-in user can delete-message
@login_required(login_url='login')
def deleteMessage(request, id):
    message = Message.objects.get(pk=id)

    # Only message-owner allowed deleting their message
    if request.user != message.user:
        return HTTPResponse("Your not allowed here !!")

    if request.method == 'POST':
        message.delete()
        return redirect('room', message.room.id)

    context = {'obj':message}
    return render(request, 'base/delete.html', context)
# ------------------------------ // End-Messages view\\ ------------------------------ #


