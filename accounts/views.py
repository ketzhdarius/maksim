from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.db.models import Sum
from rides.models import Ride
from datetime import datetime

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile_view(request):
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
def staff_add_balance(request):
    if not request.user.user_role == 'staff':
        messages.error(request, 'Access denied!')
        return redirect('home')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.balance += decimal.Decimal(amount)
            user.save()
            messages.success(request, f'Successfully added ${amount} to {user.get_full_name()}\'s balance')
        except (CustomUser.DoesNotExist, decimal.InvalidOperation):
            messages.error(request, 'Invalid user or amount')
        return redirect('staff_add_balance')

    users = CustomUser.objects.exclude(user_role='staff')
    return render(request, 'accounts/add_balance.html', {'users': users})
