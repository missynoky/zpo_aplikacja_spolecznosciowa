from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, DirectMessage, FriendRequest, Friendship
from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Notification
import re


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
        return redirect('home')

    return redirect('home')


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message_body = request.POST.get('body', '')
        files = request.FILES.getlist('files')

        for file in files:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=message_body if file == files[0] else "",
                file=file
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
    user = get_object_or_404(User, id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    is_friend = Friendship.objects.filter(
        Q(user1=request.user, user2=user) | Q(user1=user, user2=request.user)
    ).exists()

    friend_request_sent = FriendRequest.objects.filter(
        sender=request.user, receiver=user
    ).exists()

    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
        'is_friend': is_friend,
        'friend_request_sent': friend_request_sent
    }
    return render(request, 'base/profile.html', context)

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


@login_required(login_url='login')
def inbox(request):
    messages_received = DirectMessage.objects.filter(receiver=request.user).order_by('-timestamp')
    messages_sent = DirectMessage.objects.filter(sender=request.user).order_by('-timestamp')
    users = User.objects.exclude(id=request.user.id)
    context = {
        'messages_received': messages_received,
        'messages_sent': messages_sent,
        'users': users
    }
    return render(request, 'base/inbox.html', context)



@login_required(login_url='login')
def send_message(request):
    users = User.objects.exclude(id=request.user.id)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message_body = request.POST.get('message')
        receiver = get_object_or_404(User, id=user_id)

        if request.user == receiver:
            messages.error(request, "Nie możesz wysłać wiadomości do siebie!")
            return redirect('send_message')

        if message_body.strip():
            DirectMessage.objects.create(sender=request.user, receiver=receiver, message=message_body)
            messages.success(request, f"Wiadomość wysłana do @{receiver.username}")
            return redirect('inbox')

    context = {'users': users}
    return render(request, 'base/send_message.html', context)


@login_required(login_url='login')
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.user == receiver:
        return JsonResponse({"error": "Nie możesz dodać siebie do znajomych."}, status=400)

    friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)

    if not created:
        return JsonResponse({"error": "Zaproszenie zostało już wysłane."}, status=400)

    return JsonResponse({"success": "Zaproszenie wysłane!"})


@login_required(login_url='login')
def manage_friend_request(request, request_id, action):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if friend_request.receiver != request.user:
        return JsonResponse({"error": "Nie masz uprawnień do tej operacji."}, status=403)

    if action == "accept":
        friend_request.is_accepted = True
        Friendship.objects.create(user1=friend_request.sender, user2=friend_request.receiver)
        friend_request.delete()

        return JsonResponse({"success": "Znajomość zaakceptowana!"})

    elif action == "reject":
        friend_request.is_accepted = False
        friend_request.delete()
        return JsonResponse({"success": "Zaproszenie odrzucone."})

    return JsonResponse({"error": "Nieprawidłowa akcja."}, status=400)


@login_required(login_url='login')
def friend_list(request):
    friends = Friendship.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    friend_users = [friend.user1 if friend.user2 == request.user else friend.user2 for friend in friends]

    return render(request, 'base/friends_list.html', {'friends': friend_users})

@login_required(login_url='login')
def friend_requests(request):
    pending_requests = FriendRequest.objects.filter(receiver=request.user, is_accepted=None)

    return render(request, 'base/friend_request.html', {'pending_requests': pending_requests})


@login_required(login_url='login')
def remove_friend(request, user_id):
    user_to_remove = get_object_or_404(User, id=user_id)

    friendship = Friendship.objects.filter(
        Q(user1=request.user, user2=user_to_remove) | Q(user1=user_to_remove, user2=request.user)
    )

    if friendship.exists():
        friendship.delete()
        return JsonResponse({"success": "Znajomość usunięta!"})

    return JsonResponse({"error": "Nie jesteście znajomymi."}, status=400)


from .models import Photo
from .forms import PhotoForm

@login_required
def gallery_view(request, username):
    user = get_object_or_404(User, username=username)
    photos = Photo.objects.filter(user=user)
    return render(request, "base/gallery.html", {"user": user, "photos": photos})

@login_required
def upload_photo(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            return redirect("gallery", username=request.user.username)
    else:
        form = PhotoForm()
    return render(request, "base/upload_photo.html", {"form": form})


import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Photo


@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id, user=request.user)

    if request.method == "POST":
        edited_image_data = request.POST.get("edited_image")

        if edited_image_data:
            try:
                # Usuń nagłówek danych base64
                img_str = edited_image_data.split('base64,')[-1]
                img_data = base64.b64decode(img_str)

                # Utwórz nazwę pliku z rozszerzeniem
                ext = 'png'  # domyślnie PNG, bo tak zapisujemy z canvas
                filename = f"edited_{photo.id}.{ext}"

                # Zapisz nowy obraz
                photo.image.save(filename, ContentFile(img_data), save=True)

                messages.success(request, "Zdjęcie zostało zapisane!")
                return redirect("gallery", username=request.user.username)

            except Exception as e:
                messages.error(request, f"Błąd podczas zapisywania: {str(e)}")
                return redirect("edit_photo", photo_id=photo.id)

    # Dla GET pokaż formularz
    return render(request, "base/edit_photo.html", {"photo": photo})

from django.http import JsonResponse

@login_required
def delete_photo(request, photo_id):
    if request.method == "POST":
        try:
            photo = Photo.objects.get(id=photo_id, user=request.user)
            photo.delete()
            return JsonResponse({'success': True})
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Zdjęcie nie istnieje'})
    return JsonResponse({'success': False, 'error': 'Nieprawidłowa metoda'})