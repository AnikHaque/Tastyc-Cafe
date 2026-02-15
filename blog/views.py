from django.shortcuts import render, get_object_or_404
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