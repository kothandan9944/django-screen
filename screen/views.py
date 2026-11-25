from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Post
from .forms import PostForm, CommentForm, SignUpForm


class RememberLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get('remember'):
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)
        return response


def landing(request):
    return render(request, 'screen/landing.html')


def home(request):
    query = request.GET.get('q', '')
    posts = Post.objects.select_related('author').order_by('-created_at')
    if query:
        posts = posts.filter(title__icontains=query)

    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'screen/home.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'screen/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created.')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'screen/add.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('post_detail', pk=post.pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'screen/edit.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('post_detail', pk=post.pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('home')
    return render(request, 'screen/delete.html', {'post': post})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. Please login.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'screen/signup.html', {'form': form})


def posts_api(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    data = []
    for post in posts:
        data.append({
            'id': post.pk,
            'title': post.title,
            'body': post.body,
            'author': post.author.username if post.author else '',
            'image': request.build_absolute_uri(post.image.url) if post.image else '',
            'created_at': post.created_at.isoformat(),
        })
    return JsonResponse({'posts': data})


def post_detail_api(request, pk):
    post = get_object_or_404(Post.objects.select_related('author'), pk=pk)
    comments = [
        {
            'name': comment.name,
            'text': comment.text,
            'created_at': comment.created_at.isoformat(),
        }
        for comment in post.comments.order_by('-created_at')
    ]
    return JsonResponse({
        'id': post.pk,
        'title': post.title,
        'body': post.body,
        'author': post.author.username if post.author else '',
        'image': request.build_absolute_uri(post.image.url) if post.image else '',
        'created_at': post.created_at.isoformat(),
        'comments': comments,
    })