import google.generativeai as genai
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

# Gemini API কনফিগারেশন
genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
def get_ai_response(request):
    """
    AI চ্যাটবট ভিউ যা সরাসরি ডাটা প্রসেস করে।
    """
    if request.method == "POST":
        user_query = request.POST.get('message')
        
        if not user_query:
            return JsonResponse({'status': 'error', 'message': 'কোনো মেসেজ পাওয়া যায়নি।'})

        # সিস্টেম ইনস্ট্রাকশন
        instruction = f"""
        You are 'Royal Bot', the premium AI assistant of Royal Dine Restaurant. 
        Specialties: Royal Thali, Signature Kebabs, and Mughlai items.
        Policy: Open 10 AM to 11 PM. No alcohol.
        Reply briefly in the same language as the user.
        Question: {user_query}
        """

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(instruction)
            
            if response and response.text:
                return JsonResponse({'status': 'success', 'answer': response.text})
            else:
                return JsonResponse({'status': 'error', 'message': 'AI কোনো উত্তর দিতে পারেনি।'})
                
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'এআই এরর: {str(e)}'})

    # যদি ভুল করে GET রিকোয়েস্ট আসে
    return JsonResponse({'status': 'error', 'message': 'শুধুমাত্র POST রিকোয়েস্ট গ্রহণ করা হয়।'})