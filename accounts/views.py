from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.db.models import Sum
from rides.models import Ride, RideEvent
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .models import CustomUser
from .backends import CleaningModelBackend

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='accounts.backends.CleaningModelBackend')
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_view(request):
    # Handle manual distance submission for demo/testing
    if request.method == 'POST' and request.user.user_role == 'rider':
        distance_value = request.POST.get('distance')
        try:
            distance = Decimal(distance_value)
            if distance < 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, 'Please enter a valid non-negative number for distance')
            return redirect('profile')

        # Create a demo ride representing this distance (status dropped)
        demo_ride = Ride.objects.create(
            rider=request.user,
            customer=request.user,  # demo: assign to self so model constraints satisfied
            pickup_location='Manual entry',
            destination='Manual entry',
            total_distance=distance,
            price=0,
            status='dropped'
        )

        RideEvent.objects.create(
            ride=demo_ride,
            step_count=1,
            description='Manual distance added from profile (demo)'
        )

        messages.success(request, f'Manual distance {distance} km added for demo purposes')
        return redirect('profile')

    context = {
        'user': request.user
    }

    if request.user.user_role == 'rider':
        # Get total distance for all completed rides
        total_distance = Ride.objects.filter(
            rider=request.user,
            status='dropped'
        ).aggregate(total=Sum('total_distance'))['total'] or 0

        # Get today's rides and distance
        today = datetime.now().date()
        today_rides = Ride.objects.filter(
            rider=request.user,
            status='dropped',
            updated_at__date=today
        )
        today_distance = today_rides.aggregate(total=Sum('total_distance'))['total'] or 0

        context.update({
            'total_distance': total_distance,
            'today_distance': today_distance,
            'today_rides': today_rides
        })

    elif request.user.user_role == 'customer':
        # Get all rides for customer
        rides = Ride.objects.filter(customer=request.user).order_by('-created_at')
        context['rides'] = rides

    return render(request, 'accounts/profile.html', context)

@login_required
def add_funds(request):
    # Allow customers to add funds to their own balance
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError):
            messages.error(request, 'Please enter a valid positive amount')
            return redirect('add_funds')

        # Update user's balance
        user = request.user
        user.balance += amount_decimal
        user.save()
        messages.success(request, f'Added ${amount_decimal} to your balance')
        return redirect('profile')

    return render(request, 'accounts/add_funds.html')

@login_required
def staff_add_balance(request):
    if not request.user.user_role == 'staff':
        messages.error(request, 'Access denied!')
        return redirect('home')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.balance += Decimal(amount)
            user.save()
            messages.success(request, f'Successfully added ${amount} to {user.get_full_name()}\'s balance')
        except (CustomUser.DoesNotExist, InvalidOperation, TypeError):
            messages.error(request, 'Invalid user or amount')
        return redirect('staff_add_balance')

    users = CustomUser.objects.exclude(user_role='staff')
    return render(request, 'accounts/add_balance.html', {'users': users})

def logout_view(request):
    # Accept GET or POST for simplicity; perform logout and redirect to home
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('home')
