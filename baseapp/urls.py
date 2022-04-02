from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginUser, name="login"),
    path('register/', views.RegisterUser, name="register"),
    path('logout/', views.LogoutUser, name="logout"),
    path('', views.home,name="home"),
    path('room/<str:params>/', views.room,name="room"),
    path('create-room/', views.createRoom, name='create-room'), 
    path('update-room/<str:params>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:params>/', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:params>/', views.deleteMessage, name='delete-message'),
    path('profile/<str:params>/', views.userProfile, name='user-profile'),
    path('update-user/', views.updateUser, name='update-user'),
    path('topics/', views.topics, name='topics'),
    path('activities/', views.activities, name='activities'),
] 