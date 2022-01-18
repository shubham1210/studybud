
from django.contrib import messages
from django.db.models import Q
from django.forms import forms
from django.http import HttpResponse, request
from django.shortcuts import redirect, render
from django.template import context
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import RoomForm
from .models import Message, Room, Topic, User

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request,'User dosent exist')
        
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username/password dosent exsits')
            return redirect('home')

    context = {'page' : page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    return render(request,'base/login_register.html',{'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains =q) | 
        Q(name__icontains=q) |
        Q(desciption__icontains=q)
    ) 
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))

    context = {'roomsArray' : rooms ,'topics' : topics,'room_count' : room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request,id):
    SelectedRoom = Room.objects.get(id = int(id))
    room_messages = SelectedRoom.message_set.all().order_by('-created')
    participants = SelectedRoom.participants.all()
    if request.method == 'POST':
        messages = Message.objects.create( user = request.user , room = SelectedRoom , body = request.POST.get('body'))
        SelectedRoom.participants.add(request.user)
        return redirect('room', id=id)
    context = {"room" : SelectedRoom,"room_messages":room_messages,"participants":participants}
    return render(request,'base/room.html',context)


def userProfile(request,id):
    user = User.objects.get(id=int(id))
    rooms = user.room_set.all().order_by('-created')
    rooms_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user,'roomsArray':rooms,"room_messages":rooms_messages,'topics' : topics,}
    return render(request,'base/profile.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('home')
    context = {'form' : form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method =='POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if(request.method == 'POST'):
        room.delete()
        return redirect('home')
    context = {'obj': room.name}
    return render(request,'base/delete.html',context)


@login_required(login_url='login')
def deleteMessage(request,id):
    message = Message.objects.get(id=id)
    if request.user != message.user:
        return HttpResponse("You are not allowed here!")

    if(request.method == 'POST'):
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request,'base/delete.html',context)
