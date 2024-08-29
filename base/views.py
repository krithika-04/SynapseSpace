from django.shortcuts import render,redirect
from django.db.models import Q
from django.http import HttpResponse
from .models import Room,Topic,User,Message
from .forms import RoomForm,UserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def home(request):
  q= request.GET.get('q').strip() if request.GET.get('q')!=None else '' # to get the query value 
  rooms= Room.objects.filter(Q(topic__name__icontains=q)|Q(name__icontains=q)|Q(description__icontains=q)) # room contains topic and topic contains topic name with or condition
  topics= Topic.objects.all()[0:5]
  room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:3]
  rooms_count=rooms.count()
  context={'rooms':rooms,'topics':topics,'rooms_count':rooms_count,'room_messages':room_messages}
  return render(request,'base/Home.html',context)

def room(request,id):
  room = Room.objects.get(id=id)
  messages = room.message_set.all().order_by('-created') # Message.objects.filter(room__id=id)
  participants = room.participants.all()

  if request.method=='POST':
    messageToBeAdded = request.POST.get('body')
    message = Message.objects.create(body=messageToBeAdded ,room=room,user=request.user)
    room.participants.add(request.user)
    return redirect('room',id=id)

  context={'room':room,'room_messages':messages,'participants':participants}
  return render(request,'base/Room.html',context)

@login_required(login_url='login')
def createRoom(request):
  form = RoomForm() 
  topics = Topic.objects.all()
  if request.method == 'POST':
     topic_name = request.POST.get('topic')
     topic ,created = Topic.objects.get_or_create(name=topic_name)  # get the topic if you don't get topic then its created else returns the topic
     Room.objects.create(name=request.POST.get('name'),description=request.POST.get('description'),host=request.user,topic=topic)
     return redirect('home')
  context = {'form':form,'topics':topics}
  return render(request,'base/Room_Form.html',context)

def userProfile(request,id):
  user = User.objects.get(id=id)
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  topics = Topic.objects.all()
  context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
  return render(request,'base/Profile.html',context)


@login_required(login_url='login')
def updateRoom(request,id):
  room = Room.objects.get(id=id)
  form = RoomForm(instance=room) # to prefill the data while editing
  topics = Topic.objects.all() 
  if request.user != room.host:
    return HttpResponse('You are not allowed')

  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic ,created = Topic.objects.get_or_create(name=topic_name)  
    room.name= request.POST.get('name')
    room.description= request.POST.get('description')
    room.topic= topic
    room.save()
    return redirect('home')
  context = {'form':form,'topics':topics,'room':room}
  return render(request,'base/Room_Form.html',context)

@login_required(login_url='login')
def deleteRoom(request,id):
  room = Room.objects.get(id=id)
  if request.user != room.host:
    return HttpResponse('You are not allowed')
  if request.method == 'POST':
    room.delete()
    return redirect('home')
  context = {'obj':room}
  return render(request,'base/Delete.html',context)

@login_required(login_url='login')
def deleteMessage(request,id):
  message = Message.objects.get(id=id)
  if request.user != message.user:
    return HttpResponse('You are not allowed')
  if request.method == 'POST':
    message.delete()
    return redirect('home')
  context = {'obj':message}
  return render(request,'base/Delete.html',context)

def loginPage(request):
  page='login'
  if request.user.is_authenticated:
    return redirect('home')
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
      user = User.objects.get(username=username) #chk user exists
    except:
      messages.error(request, "user does not exist")
    user = authenticate(request,username=username,password=password)
    if user!=None:
      login(request,user) #create session
      return redirect('home')
    else:
      messages.error(request, "username or password is incorrect")
  context={'page':page}
  return render(request,'base/Login_Register.html',context)

def logoutPage(request):
  logout(request)
  return redirect('home')

def registerPage(request):
  form= UserCreationForm()
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)  # to get the user created
      user.save()
      login(request,user)
      return redirect('home')
    else:
      messages.error(request,'Error occured while creating user')
  context = {'form':form}
  return render(request,'base/Login_Register.html',context)

@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)
  if request.method=='POST':
    form = UserForm(request.POST,instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile',id=user.id)
  context={'form':form}
  return render(request,'base/Update-User.html',context)

def topicsPage(request):
  q= request.GET.get('q') if request.GET.get('q')!=None else ''
  topics = Topic.objects.filter(Q(name__icontains=q))
  print(topics)
  context={'topics':topics}
  return render(request,'base/Topics.html',context)

def activityPage(request):
  room_messages = Message.objects.all()[0:3]
  context={'room_messages':room_messages}
  return render(request,'base/Activity.html',context)