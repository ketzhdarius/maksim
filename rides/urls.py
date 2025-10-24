from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_ride, name='create_ride'),
    path('', views.ride_list, name='ride_list'),
    path('<int:pk>/', views.ride_detail, name='ride_detail'),
    path('<int:pk>/accept/', views.accept_ride, name='accept_ride'),
    path('<int:pk>/complete/', views.complete_ride, name='complete_ride'),
    path('calculate-distance/', views.calculate_distance, name='calculate_distance'),
]
