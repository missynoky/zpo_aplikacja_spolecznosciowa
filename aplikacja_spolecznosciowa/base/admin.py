from django.contrib import admin
from .models import Room, Topic, Message, User, FriendRequest, Friendship


admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(FriendRequest)
admin.site.register(Friendship)
