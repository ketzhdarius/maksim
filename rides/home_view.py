from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rides.models import Ride

@login_required
def home_view(request):
    context = {}

    if request.user.user_role == 'rider':
        # Show available rides for riders
        context['available_rides'] = Ride.objects.filter(status='created')
    elif request.user.user_role == 'customer':
        # Show customer's own rides
        context['rides'] = request.user.rides_as_customer.all()

    return render(request, 'home.html', context)
