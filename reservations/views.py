from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Reservation, TableCapacity

def book_table(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        guests = int(request.POST.get('guests'))
        date = request.POST.get('date')
        shift = request.POST.get('shift')

        # লজিক: ওই দিনের ওই শিফটের ক্যাপাসিটি চেক করা
        capacity, created = TableCapacity.objects.get_or_create(
            date=date, shift=shift, defaults={'total_tables': 10}
        )

        if capacity.available_tables > 0:
            # বুকিং সেভ করা
            res = Reservation.objects.create(
                user=request.user, name=name, email=email, 
                phone=phone, guest_count=guests, date=date, shift=shift
            )
            # টেবিল কাউন্ট আপডেট করা
            capacity.booked_tables += 1
            capacity.save()
            
            messages.success(request, f"Table booked! Your ID: {res.booking_id}")
            return redirect('reservation_success', booking_id=res.booking_id)
        else:
            messages.error(request, "Sorry! No tables available for this slot.")
    
    return render(request, 'reservation.html')


# --- এই ফাংশনটি মিসিং ছিল, এটি যোগ করুন ---
def reservation_success(request, booking_id):
    reservation = get_object_or_404(Reservation, booking_id=booking_id)
    return render(request, 'reservation_success.html', {'reservation': reservation})