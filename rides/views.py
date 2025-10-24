from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Ride, RideEvent
from .forms import RideForm
import random

@login_required
def create_ride(request):
    if request.user.user_role != 'customer':
        messages.error(request, 'Only customers can create rides')
        return redirect('home')

    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.customer = request.user

            # Check if customer has enough balance
            if ride.price > request.user.balance:
                messages.error(request, 'Insufficient balance to create this ride')
                return render(request, 'rides/create_ride.html', {'form': form})

            ride.save()

            # Create initial ride event
            RideEvent.objects.create(
                ride=ride,
                step_count=1,
                description="User created a ride."
            )

            messages.success(request, 'Ride created successfully!')
            return redirect('ride_detail', pk=ride.pk)
    else:
        form = RideForm()

    return render(request, 'rides/create_ride.html', {'form': form})

@login_required
def ride_list(request):
    if request.user.user_role == 'customer':
        rides = Ride.objects.filter(customer=request.user)
    elif request.user.user_role == 'rider':
        rides = Ride.objects.filter(status='created')
    else:  # staff
        rides = Ride.objects.all()

    return render(request, 'rides/ride_list.html', {'rides': rides})

@login_required
def ride_detail(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    events = ride.events.all().order_by('step_count')
    return render(request, 'rides/ride_detail.html', {'ride': ride, 'events': events})

@login_required
def accept_ride(request, pk):
    if request.user.user_role != 'rider':
        messages.error(request, 'Only riders can accept rides')
        return redirect('home')

    ride = get_object_or_404(Ride, pk=pk)

    if ride.status != 'created':
        messages.error(request, 'This ride is no longer available')
        return redirect('ride_list')

    with transaction.atomic():
        ride.rider = request.user
        ride.status = 'assigned'
        ride.save()

        RideEvent.objects.create(
            ride=ride,
            step_count=2,
            description=f"Ride accepted by {request.user.get_full_name()}"
        )

    messages.success(request, 'Ride accepted successfully!')
    return redirect('ride_detail', pk=pk)

@login_required
def complete_ride(request, pk):
    ride = get_object_or_404(Ride, pk=pk)

    if request.user != ride.rider:
        messages.error(request, 'You are not authorized to complete this ride')
        return redirect('ride_list')

    if ride.status != 'assigned':
        messages.error(request, 'Invalid ride status')
        return redirect('ride_detail', pk=pk)

    with transaction.atomic():
        # Update ride status
        ride.status = 'dropped'
        ride.save()

        # Transfer balance from customer to rider
        customer = ride.customer
        rider = ride.rider

        customer.balance -= ride.price
        rider.balance += ride.price

        customer.save()
        rider.save()

        # Create completion event
        RideEvent.objects.create(
            ride=ride,
            step_count=3,
            description="Ride completed successfully"
        )

    messages.success(request, 'Ride completed successfully!')
    return redirect('ride_detail', pk=pk)

def calculate_distance(request):
    """AJAX view to calculate random distance"""
    if request.method == 'POST':
        return JsonResponse({'distance': random.uniform(10, 30)})
