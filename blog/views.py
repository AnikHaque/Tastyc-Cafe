from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Blog

# All Blogs List Page
def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

# Blog Details Page
def blog_detail(request, slug):
    # Slug diye specific blog khuje ber kora hobe
    blog = get_object_or_404(Blog, slug=slug)
    # Related blogs (optional: niche show koranor jonno)
    related_blogs = Blog.objects.filter(is_published=True).exclude(id=blog.id)[:3]
    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs
    })

@staff_member_required # শুধুমাত্র স্টাফরা এই পেজ এক্সেস করতে পারবে
def create_blog(request):
    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category')
        content = request.POST.get('content')
        thumbnail = request.FILES.get('thumbnail')
        
        # ডাটাবেজে সেভ করা
        blog = Blog.objects.create(
            title=title,
            category=category,
            content=content,
            thumbnail=thumbnail,
            author=request.user
        )
        return redirect('blog_list')
        
    return render(request, 'blog/create_blog.html')