from orders.models import OrderItem
from menu.models import Food
from django.db.models import Count

def get_ai_recommendations(food_item, limit=4):
    # এই খাবারটি যেসব অর্ডারে কেনা হয়েছে সেই অর্ডার আইডিগুলো বের করা
    order_ids = OrderItem.objects.filter(food=food_item).values_list('order_id', flat=True)
    
    # ওই একই অর্ডারগুলোতে অন্য আর কি কি খাবার ছিল তা বের করা
    recommendations = Food.objects.filter(
        orderitem__order_id__in=order_ids
    ).exclude(id=food_item.id).annotate(
        count=Count('id')
    ).order_by('-count')[:limit]
    
    return recommendations