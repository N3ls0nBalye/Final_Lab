from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import DeleteView
from .models import BlogPost, Category, Comment, Like
from .forms import CreateBlogPostForm, UpdateBlogPostForm
from account.models import Account
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.forms import CommentForm
from django.contrib.auth.decorators import login_required

def create_blog_view(request):
    context = {}
    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')

    form = CreateBlogPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        author = Account.objects.filter(email=user.email).first()
        obj.author = author
        obj.save()
        form = CreateBlogPostForm()

    context['form'] = form
    return render(request, "blog/create_blog.html", context)


def detail_blog_view(request, slug):
    context = {}
    blog_post = get_object_or_404(BlogPost, slug=slug)
    context['blog_post'] = blog_post
    return render(request, 'blog/detail_blog.html', context)


def edit_blog_view(request, slug):
    context = {}
    user = request.user
    if not user.is_authenticated:
        return redirect("must_authenticate")

    blog_post = get_object_or_404(BlogPost, slug=slug)

    if blog_post.author != user:
        return HttpResponse('You are not the author of that post.')

    if request.POST:
        form = UpdateBlogPostForm(request.POST or None, request.FILES or None, instance=blog_post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Updated"
            blog_post = obj

    form = UpdateBlogPostForm(
        initial={
            "title": blog_post.title,
            "body": blog_post.body,
            "image": blog_post.image,
            "category": blog_post.category,  # Ensure category is passed into the form
        }
    )

    context['form'] = form
    return render(request, 'blog/edit_blog.html', context)



class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'blog/blog_confirm_delete.html'  # Create this template
    success_url = reverse_lazy('blog:create')  # Redirect to blog list after deletion

    def get_queryset(self):
        """Ensure only the blog post owner can delete it"""
        return self.model.objects.filter(author=self.request.user)



def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:detail', slug=slug)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form})

@login_required
def like_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()  # Unlike if already liked
    return redirect('blog:detail', slug=slug)



def get_blog_queryset(query=None):
    queryset = []
    queries = query.split(" ") 

    # Get categories that match the query
    categories = Category.objects.filter(name__icontains=query)
    
    for q in queries:
        # Search posts by title, body, and category name
        posts = BlogPost.objects.filter(
            Q(title__icontains=q) | 
            Q(body__icontains=q) | 
            Q(category__name__icontains=q)  # Add category name filter here
        ).distinct()

        for post in posts:
            queryset.append(post)

    # Return unique posts by converting to a set and then back to a list
    return list(set(queryset))


