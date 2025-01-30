from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Notification
import re

# rooms = [
#     { 'id':1, 'name':'Moje konto'},
#     { 'id':2, 'name':'Aktualności'},
#     { 'id':3, 'name':'Moi znajomi'},
#
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'Użytkownik nie istnieje')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nazwa użytkownika lub hasło nie istnieje')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Błąd podczas rejestracji')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''


    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    notifications_count = 0
    if request.user.is_authenticated:
        notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {'rooms': rooms, 'topics':topics, 'room_count': room_count,
               'room_messages' : room_messages,
               'notifications_count': notifications_count}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user != message.user:
        return redirect('home')

    if request.method == "POST":
        message.body = request.POST.get('body')
        message.save()
        return redirect('home')  # Przekierowanie na stronę główną po zapisaniu

    return redirect('home')  # Jeśli nie był to POST, wracamy na główną




def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message_body = request.POST.get('body')
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=message_body
        )
        room.participants.add(request.user)

        if request.user != room.host:
            Notification.objects.create(
                user=room.host,
                sender=request.user,
                message=f"{request.user.username} dodał nową wiadomość w {room.name}.",
                link=f"/room/{room.id}"
            )

        if ">>" in message_body:
            reply_to_id = message_body.split(">>")[1].split()[0]
            try:
                replied_message = Message.objects.get(id=reply_to_id)
                if replied_message.user != request.user:
                    Notification.objects.create(
                        user=replied_message.user,
                        sender=request.user,
                        message=f"{request.user.username} odpowiedział na Twoją wiadomość w {room.name}.",
                        link=f"/room/{room.id}#message-{replied_message.id}"
                    )
            except Message.DoesNotExist:
                pass

        mentioned_users = re.findall(r"@(\w+)", message_body)
        for username in mentioned_users:
            try:
                mentioned_user = User.objects.get(username=username)
                if mentioned_user != request.user:
                    Notification.objects.create(
                        user=mentioned_user,
                        sender=request.user,
                        message=f"{request.user.username} wspomniał Cię w wiadomości w {room.name}.",
                        link=f"/room/{room.id}#message-{message.id}"
                    )
            except User.DoesNotExist:
                pass

        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)



def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render (request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form_update.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Nie masz dostępu do tej strony')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Nie masz dostępu do tej strony')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)


    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


@login_required(login_url='login')
def notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'base/notifications.html', {'notifications': notifications})
