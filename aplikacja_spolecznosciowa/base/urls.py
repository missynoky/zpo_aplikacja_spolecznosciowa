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

path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
path('manage_friend_request/<int:request_id>/<str:action>/', views.manage_friend_request,
         name='manage_friend_request'),
path('friends/', views.friend_list, name='friend_list'),
path('friend_requests/', views.friend_requests, name='friend_requests'),
path('remove_friend/<int:user_id>/', views.remove_friend, name='remove_friend'),


]