from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import AboutFeature, AboutStory, Chef, ContactMessage
from core.models import AboutSection, HeroSection, RestaurantFeature
from menu.forms import TestimonialForm
from menu.models import Category, ComboDeal, Food, Offer, Testimonial
from blog.models import Blog
from orders.models import Coupon, OrderItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from menu.models import FlashDeal



def home(request):
    # Categories with available food count
    categories = Category.objects.annotate(
        item_count=Count('foods', filter=Q(foods__is_available=True))
    )

  # ১. প্রথমে টপ সেলিং ফুড আইডিগুলো বের করি
    top_food_ids = (
        OrderItem.objects
        .filter(food__is_available=True)
        .values('food')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')
        .values_list('food', flat=True)[:8]
    )

    # ২. ওই আইডিগুলো দিয়ে সরাসরি Food অবজেক্ট নিয়ে আসি
    if top_food_ids:
        top_selling = Food.objects.filter(id__in=top_food_ids)
        # এখানে অর্ডারিং ঠিক রাখার জন্য (যাতে টপ সেলিংটা আগে থাকে)
        top_selling = sorted(top_selling, key=lambda t: list(top_food_ids).index(t.id))
    else:
        top_selling = Food.objects.filter(is_available=True)[:8]

    # Today Specials
    today_specials = Food.objects.filter(is_today_special=True, is_available=True)[:8]

    # Active Offers
    today = timezone.now().date()
    offers = Offer.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
        food__is_available=True
    ).select_related('food')
    combos = ComboDeal.objects.filter(is_active=True)
    testimonials = Testimonial.objects.all().order_by('-created_at')
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')[:6]
    flash_deal = FlashDeal.objects.filter(is_active=True).first()
    # core অ্যাপের মডেল থেকে ডাটা নিয়ে আসা
    hero = HeroSection.objects.filter(is_active=True).last()
    features = RestaurantFeature.objects.all()
    about = AboutSection.objects.last() # লাস্ট ডাটাটি নিবে

    active_coupon = Coupon.objects.filter(
        active=True, 
        valid_to__gte=timezone.now()
    ).first()
    context = {
       'hero': hero,
        'features': features,
        'about': about,
        "categories": categories,
        'active_coupon': active_coupon,
        "top_selling": top_selling,
        "today_specials": today_specials,
        "offers": offers,
        'testimonials': testimonials,
        'blogs': blogs,
        'combos': combos,
        'flash_deal':flash_deal
    }

    return render(request, "home.html", context)

@login_required
def add_review(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user  # বর্তমান লগইন করা ইউজারকে সেট করা হলো
            # যদি আপনি চান ইউজারের নাম এবং ডেজিগনেশন প্রোফাইল থেকে অটো আসবে:
            testimonial.name = request.user.get_full_name() or request.user.username
            testimonial.save()
            messages.success(request, "Review add hoyeche!")
            return redirect('my_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'add_review.html', {'form': form})

@login_required
def my_testimonials(request):
    # এখন এই লাইনটি আর এরর দিবে না
    user_testimonials = Testimonial.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_testimonials.html', {'my_testimonials': user_testimonials})


def about(request):
    story = AboutStory.objects.first() # ডাটাবেস থেকে প্রথম স্টোরিটা নিচ্ছে
    features = AboutFeature.objects.all() # সব ফিচার নিচ্ছে
    chefs = Chef.objects.all().order_by('order') # সব শেফ নিচ্ছে
    
    # এই context ডিকশনারিটিই ডাটাগুলোকে HTML এ পাঠায়
    context = {
        'story': story,
        'features': features,
        'chefs': chefs
    }
    return render(request, 'about.html', context)


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # মেসেজ সেভ করার লজিক
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
        
    return render(request, 'contact.html')

from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

# ইমেইল পাঠানোর প্রয়োজনীয় ইম্পোর্টস
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def custom_email_sender(request):
    """
    এই ভিউটি একটি কাস্টম ফর্ম থেকে ডাটা নিয়ে লাক্সারি টেম্পলেটে ইমেইল পাঠায়।
    """
    if request.method == "POST":
        # ১. ফর্ম থেকে ডাটা রিসিভ করা
        s_name = request.POST.get('sender_name')
        s_email = request.POST.get('sender_email')
        r_email = request.POST.get('receiver_email')
        subject = request.POST.get('subject')
        msg_body = request.POST.get('message')

        # ২. HTML টেম্পলেট লোড করা (আপনার গ্লোবাল templates/emails/ ফোল্ডার থেকে)
        # নিশ্চিত করুন dynamic_email.html ফাইলটি templates/emails/ এর ভেতর আছে
        try:
            html_content = render_to_string('emails/dynamic_email.html', {
                'sender_name': s_name,
                'sender_email': s_email,
                'message_body': msg_body,
            })
            text_content = strip_tags(html_content)

            # ৩. প্রেরকের ঠিকানা সেট করা (settings.py এর DEFAULT_FROM_EMAIL ব্যবহার করে)
            # ফরম্যাট: "Name <email@example.com>"
            from_email_formatted = f"{s_name} <{settings.DEFAULT_FROM_EMAIL}>"

            # ৪. ইমেইল অবজেক্ট তৈরি করা
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email_formatted,
                to=[r_email],
                # গ্রাহক রিপ্লাই দিলে যেন ইউজারের ইমেইলে যায়
                reply_to=[s_email],
            )
            email.attach_alternative(html_content, "text/html")

            # ৫. ইমেইল পাঠানো
            # fail_silently=False দেওয়া হয়েছে যাতে কোনো এরর থাকলে জ্যাঙ্গো সেটি দেখায়
            email.send(fail_silently=False)
            
            messages.success(request, f"সাফল্যের সাথে {r_email} ঠিকানায় মেইল পাঠানো হয়েছে! মেইলট্র্যাপ ইনবক্স চেক করুন।")

        except Exception as e:
            # কোনো এরর হলে সেটি মেসেজ হিসেবে দেখাবে
            messages.error(request, f"মেইল পাঠানো যায়নি। কারিগরি ত্রুটি: {str(e)}")

    # আপনার ফর্ম পেজটি রেন্ডার করা (templates/emails/email_form_page.html)
    return render(request, 'emails/email_form_page.html')