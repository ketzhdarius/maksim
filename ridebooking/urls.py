from django.contrib import admin
from django.urls import path, include
from rides.home_view import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('rides/', include('rides.urls')),
    path('dashboard/', include('dashboard.urls')),
]
