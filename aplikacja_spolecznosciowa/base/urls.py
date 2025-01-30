from tkinter.font import names

from django.urls import path
from . import views

urlpatterns  = [
path('login/', views.loginPage, name="login"),
path('logout/', views.logoutUser, name="logout"),
path('register/', views.registerPage, name="register"),

path('', views.home, name='home'),
path('edit-message/<int:message_id>/', views.edit_message, name='edit-message'),
path('room/<str:pk>/', views.room, name='room'),
path('profile/<str:pk>/', views.userProfile, name='user-profile'),

path('create-room/', views.createRoom, name='create-room'),
path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

path('update-user/', views.updateUser, name="update-user"),

path('topics/', views.topicsPage, name="topics"),
path('activity/', views.activityPage, name="activity"),
path('notifications/', views.notifications, name='notifications'),
path('inbox/', views.inbox, name='inbox'),
path('send_message/', views.send_message, name='send_message'),




]