from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns  = [
path('login/', views.loginPage, name="login"),
path('logout/', views.logoutUser, name="logout"),
path('register/', views.registerPage, name="register"),

    path("gallery/<str:username>/", views.gallery_view, name="gallery"),
    path("upload/", views.upload_photo, name="upload-photo"),
    path("edit/<int:photo_id>/", views.edit_photo, name="edit-photo"),
path('delete-photo/<int:photo_id>/', views.delete_photo, name='delete-photo'),


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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)