import qrcode
import base64
from io import BytesIO
from datetime import date as dt_date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

# আপনার অ্যাপের মডেলগুলো ইমপোর্ট
from .models import Reservation, TableCapacity

@login_required
def book_table(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        shift = request.POST.get('shift')
        guests = int(request.POST.get('guests'))
        
        # আমরা ধরে নিচ্ছি আপনার রেস্টুরেন্টে সর্বোচ্চ ২০ জনের বেশি একসাথে বুকিং দেওয়া যাবে না
        if guests > 20:
            messages.error(request, "Sorry, we cannot accommodate more than 20 guests in a single booking.")
            return render(request, 'tablebooking/reservation.html', {'today': dt_date.today()})

        with transaction.atomic():
            capacity, created = TableCapacity.objects.get_or_create(
                date=date, shift=shift, defaults={'total_tables': 15}
            )

            # স্মার্ট চেক: টেবিল খালি আছে কি না
            if capacity.available_tables > 0:
                # বুকিং সেভ
                res = Reservation.objects.create(
                    user=request.user, name=request.POST.get('name'),
                    email=request.POST.get('email'), phone=request.POST.get('phone'),
                    guest_count=guests, date=date, shift=shift
                )
                capacity.booked_tables += 1
                capacity.save()
                return redirect('reservation_success', booking_id=res.booking_id)
            else:
                # এরর মেসেজ যদি টেবিল না থাকে
                messages.error(request, f"Full! No tables available for {date} during {shift} shift.")
    
    return render(request, 'tablebooking/reservation.html', {'today': dt_date.today()})

def reservation_success(request, booking_id):
    # ডাটাবেস থেকে বুকিং খুঁজে বের করা
    reservation = get_object_or_404(Reservation, booking_id=booking_id)
    
    # ৫. কিউআর কোড জেনারেট করা
    qr_content = f"ID: {reservation.booking_id}\nName: {reservation.name}\nDate: {reservation.date}\nShift: {reservation.shift}"
    
    qr = qrcode.QRCode(version=1, border=2, box_size=10)
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # ইমেজকে টেক্সট ফরম্যাটে (base64) রূপান্তর যাতে HTML এ সরাসরি দেখানো যায়
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    context = {
        'reservation': reservation,
        'qr_code': qr_code_base64
    }
    return render(request, 'tablebooking/success.html', context)


@login_required
def my_bookings(request):
    """ইউজার তার নিজের সব বুকিং এখানে দেখতে পাবে"""
    bookings = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tablebooking/my_bookings.html', {'bookings': bookings})

from django.http import JsonResponse

def check_availability(request):
    date = request.GET.get('date')
    shift = request.GET.get('shift')
    capacity = TableCapacity.objects.filter(date=date, shift=shift).first()
    
    if capacity:
        available = capacity.available_tables
    else:
        available = 15 # যদি ওই দিনের ডাটা না থাকে, তবে ডিফল্ট ১৫টি টেবিল খালি
        
    return JsonResponse({'available': available})