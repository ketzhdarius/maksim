from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/add-balance/', views.staff_add_balance, name='staff_add_balance'),
    path('add-funds/', views.add_funds, name='add_funds'),
]
