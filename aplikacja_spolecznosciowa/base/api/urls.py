from django.urls import path
from . import views
from ..urls import urlpatterns

urlpatterns = [
    path('', views.getRoutes),
    path('rooms/', views.getRooms),
    path('rooms/<str:pk>/', views.getRoom)
]