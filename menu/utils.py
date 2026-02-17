# menu/utils.py
from django.db.models import Count
from .models import Food, Category
# এখানে আপনার অর্ডারের অ্যাপ থেকে OrderItem ইম্পোর্ট করুন (ধরে নিচ্ছি অ্যাপের নাম orders)
try:
    from orders.models import OrderItem 
except ImportError:
    OrderItem = None

def get_ai_recommendations(user, limit=4):
    """ইউজারের পছন্দ অনুযায়ী খাবার সাজেস্ট করার লজিক"""
    
    # ১. ইউজার লগইন না থাকলে বা অর্ডার ডাটা না থাকলে স্পেশাল খাবার দেখাবে
    if not user.is_authenticated or OrderItem is None:
        return Food.objects.filter(is_available=True, is_today_special=True).order_for_eval().order_by('?')[:limit]

    # ২. ইউজার কোন ক্যাটাগরি বেশি অর্ডার করেছে তা খুঁজে বের করা
    favorite_categories = Category.objects.filter(
        foods__orderitem__order__user=user
    ).annotate(
        cat_count=Count('foods__orderitem')
    ).order_by('-cat_count')[:2]

    # ৩. রিকমেন্ডেশন তৈরি
    if favorite_categories.exists():
        # ওই ক্যাটাগরির খাবার যা ইউজার এখনো কেনেনি
        recommended = Food.objects.filter(
            category__in=favorite_categories,
            is_available=True
        ).exclude(
            orderitem__order__user=user
        ).distinct().order_by('?')[:limit]
        
        # যদি ৪টার কম হয়, তবে স্পেশাল খাবার দিয়ে মেকআপ করা
        res_list = list(recommended)
        if len(res_list) < limit:
            extra = Food.objects.filter(is_today_special=True).exclude(
                id__in=[f.id for f in res_list]
            ).order_by('?')[:(limit - len(res_list))]
            res_list.extend(list(extra))
        return res_list

    # ৪. কোনো ডাটা না থাকলে ডিফল্ট স্পেশাল খাবার
    return Food.objects.filter(is_available=True, is_today_special=True).order_by('?')[:limit]