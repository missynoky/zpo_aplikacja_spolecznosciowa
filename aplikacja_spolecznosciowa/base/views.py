from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

rooms = [
    { 'id':1, 'name':'Moje konto'},
    { 'id':2, 'name':'Aktualności'},
    { 'id':3, 'name':'Moi znajomi'},

]

def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = None
    for i in rooms:
        if i['id'] == int(pk):
            room = i
    context = {'room' : room}

    return render(request, 'base/room.html', context)
