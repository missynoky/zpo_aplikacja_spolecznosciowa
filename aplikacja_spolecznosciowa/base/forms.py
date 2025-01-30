from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']
        labels = {
            'name': 'Nazwa',
            'username': 'Nazwa użytkownika',
            'email': 'Adres e-mail',
            'password1': 'Hasło',
            'password2': 'Powtórz hasło',
        }


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
        labels = {
            'name': 'Nazwa',
            'avatar': 'Zdjęcie profilowe',
            'username': 'Nazwa użytkownika',
            'email': 'Adres e-mail',
            'bio': 'Opis'
        }