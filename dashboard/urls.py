from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/add-balance/', views.add_balance, name='add_balance'),
    path('statistics/', views.ride_statistics, name='ride_statistics'),
]
