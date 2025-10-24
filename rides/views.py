from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Ride, RideEvent
from .forms import RideForm
import random
from decimal import Decimal, InvalidOperation
from django.db.models import Max

PRICE_PER_KM = Decimal('20.00')  # 20 PHP per km (not used here but kept)

@login_required
def create_ride(request):
    if request.user.user_role != 'customer':
        messages.error(request, 'Only customers can create rides')
        return redirect('home')

    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)

            # Use provided distance (should be filled by AJAX) and provided price
            try:
                distance = Decimal(form.cleaned_data.get('total_distance') or 0)
                price = Decimal(form.cleaned_data.get('price') or 0)
                if distance < 0 or price < 0:
                    raise InvalidOperation
            except (InvalidOperation, TypeError):
                form.add_error(None, 'Enter valid non-negative numbers for distance and price')
                return render(request, 'rides/create_ride.html', {'form': form})

            # Ensure user has enough balance to cover the price
            if price > request.user.balance:
                form.add_error('price', 'Price exceeds your available balance')
                return render(request, 'rides/create_ride.html', {'form': form})

            ride.total_distance = distance
            ride.price = price
            ride.customer = request.user
            ride.status = 'created'
            ride.save()

            # Create initial ride event with dynamic step_count
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
    # Accepting a ride must be a POST action
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

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

        # compute next step_count
        last_step = ride.events.aggregate(max_step=Max('step_count'))['max_step'] or 0
        RideEvent.objects.create(
            ride=ride,
            step_count=last_step + 1,
            description=f"Ride accepted by {request.user.get_full_name()}"
        )

    messages.success(request, 'Ride accepted successfully!')
    return redirect('ride_detail', pk=pk)


@login_required
def complete_ride(request, pk):
    # Completing a ride must be a POST action
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    ride = get_object_or_404(Ride, pk=pk)

    if request.user != ride.rider:
        messages.error(request, 'You are not authorized to complete this ride')
        return redirect('ride_list')

    if ride.status != 'assigned':
        messages.error(request, 'Invalid ride status')
        return redirect('ride_detail', pk=pk)

    with transaction.atomic():
        # Transfer balance from customer to rider using Decimal arithmetic
        customer = ride.customer
        rider = ride.rider
        try:
            price = Decimal(ride.price)
        except (InvalidOperation, TypeError):
            messages.error(request, 'Invalid ride price stored. Please contact support.')
            return redirect('ride_detail', pk=pk)

        # Ensure customer still has sufficient balance
        if customer.balance < price:
            messages.error(request, 'Customer has insufficient balance to complete this ride.')
            return redirect('ride_detail', pk=pk)

        # Update ride status first
        ride.status = 'dropped'
        ride.save()

        # Transfer funds
        customer.balance = (Decimal(customer.balance) - price).quantize(Decimal('0.01'))
        rider.balance = (Decimal(rider.balance) + price).quantize(Decimal('0.01'))

        customer.save()
        rider.save()

        # create completion event with incremented step_count
        last_step = ride.events.aggregate(max_step=Max('step_count'))['max_step'] or 0
        RideEvent.objects.create(
            ride=ride,
            step_count=last_step + 1,
            description="Ride completed successfully"
        )

    messages.success(request, 'Ride completed successfully!')
    return redirect('ride_detail', pk=pk)


def calculate_distance(request):
    """AJAX view to calculate random distance"""
    if request.method == 'POST':
        distance = random.uniform(10, 30)
        # Return a rounded float value
        return JsonResponse({'distance': round(distance, 2)})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
