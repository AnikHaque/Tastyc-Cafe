from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Blog,Comment
from django.utils.text import slugify

# All Blogs List Page
def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
    # আগে ছিল 'blog/blog_list.html', এখন সরাসরি ফাইল নাম
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    related_blogs = Blog.objects.filter(is_published=True).exclude(id=blog.id)[:4]
    
    if request.method == "POST":
        if request.user.is_authenticated:
            text = request.POST.get('comment')
            Comment.objects.create(blog=blog, user=request.user, text=text)
            return redirect('blog_detail', slug=slug)
        else:
            return redirect('login') # ইউজার লগইন না থাকলে
            
    return render(request, 'blog/blog_detail.html', {
        'blog': blog, 
        'related_blogs': related_blogs
    })

@staff_member_required
def create_blog(request): # এই যে এখানে 'request' প্যারামিটার
    if request.method == "POST":
        # ফর্ম থেকে ডাটা রিসিভ করা হচ্ছে
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        read_time = request.POST.get('read_time', 5)
        tags = request.POST.get('tags', '')
        thumbnail = request.FILES.get('thumbnail') # ইমেজের জন্য FILES ব্যবহার করতে হয়
        
        # টাইটেল থেকে স্লাগ তৈরি করা (যাতে NoReverseMatch এরর না আসে)
        generated_slug = slugify(title)
        
        # ডাটাবেজে সেভ করা
        Blog.objects.create(
            title=title,
            slug=generated_slug,
            content=content,
            category=category,
            read_time=read_time,
            tags=tags,
            thumbnail=thumbnail,
            author=request.user # বর্তমানে লগইন করা ইউজারই লেখক
        )
        
        # সেভ হওয়ার পর ব্লগ লিস্ট পেজে চলে যাবে
        return redirect('home')
    
    # যদি মেথড GET হয়, তবে জাস্ট পেজটা দেখাবে
    return render(request, 'blog/create_blog.html')