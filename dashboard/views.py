from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from rides.models import Ride, RideEvent
from accounts.forms import CustomUserCreationForm
from django.db.models import Sum
from decimal import Decimal, InvalidOperation

@login_required
def dashboard_home(request):
    if request.user.user_role != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    total_users = CustomUser.objects.count()
    total_rides = Ride.objects.count()
    completed_rides = Ride.objects.filter(status='dropped').count()
    active_rides = Ride.objects.filter(status='assigned').count()

    context = {
        'total_users': total_users,
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'active_rides': active_rides,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def user_list(request):
    if request.user.user_role != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    users = CustomUser.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users})

@login_required
def create_user(request):
    if request.user.user_role != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('dashboard:user_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'dashboard/create_user.html', {'form': form})

@login_required
def add_balance(request):
    if request.user.user_role != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')

        try:
            user = CustomUser.objects.get(id=user_id)
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise ValueError('Amount must be positive')

            user.balance += amount_decimal
            user.save()
            messages.success(request, f'Successfully added ${amount} to {user.get_full_name()}\'s balance')

        except (CustomUser.DoesNotExist, ValueError, InvalidOperation) as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('dashboard:add_balance')

    users = CustomUser.objects.exclude(user_role='staff')
    return render(request, 'dashboard/add_balance.html', {'users': users})

@login_required
def ride_statistics(request):
    if request.user.user_role != 'staff':
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')

    total_earnings = Ride.objects.filter(status='dropped').aggregate(total=Sum('price'))['total'] or 0
    riders = CustomUser.objects.filter(user_role='rider')
    rider_stats = []

    for rider in riders:
        completed_rides = Ride.objects.filter(rider=rider, status='dropped')
        total_distance = completed_rides.aggregate(total=Sum('total_distance'))['total'] or 0
        earnings = completed_rides.aggregate(total=Sum('price'))['total'] or 0

        rider_stats.append({
            'rider': rider,
            'completed_rides': completed_rides.count(),
            'total_distance': total_distance,
            'earnings': earnings
        })

    context = {
        'total_earnings': total_earnings,
        'rider_stats': rider_stats
    }
    return render(request, 'dashboard/ride_statistics.html', context)
