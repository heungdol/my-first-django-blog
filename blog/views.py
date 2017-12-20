from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Comment
from .forms import PostForm, CommentForm

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

import json

def main (request) :
    return render(request, 'blog/main.html')

def post_list(request) :
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk) :
    post = get_object_or_404(Post, pk=pk)
    sponsors = []
    if (post.user_sponsors != None) :
        sponsors = json.loads(post.user_sponsors)
    informant = post.user_informant
    
    return render(request, 'blog/post_detail.html', {'post': post, 'sponsors': sponsors, 'info': informant})

@login_required
def post_new (request):
    if (request.method == "POST") :
        form = PostForm(request.POST)
        if form.is_valid() :
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else :
        form = PostForm() 
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit (request, pk):
    post = get_object_or_404(Post, pk=pk)
    if (post.author != request.user) :
        return redirect('post_detail', pk=post.pk)
    
    if (request.method == "POST") :
        form = PostForm(request.POST, instance=post)
        if form.is_valid() :
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else :
        form = PostForm(instance=post) 
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True, author=request.user).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

def publish(self):
    self.published_date = timezone.now()
    self.save()
    
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if (post.author != request.user) :
        return redirect('post_detail', pk=post.pk)
    
    post.delete()
    return redirect('post_list')

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if (str(comment.author) == str(request.user)) :
        comment.approve()

    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if (str(comment.author) == str(request.user)) :
        comment.delete()
    
    return redirect('post_detail', pk=comment.post.pk)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('main')
    else:
        form = UserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})

@login_required
def add_user_sponsor(request, pk) :
    post = get_object_or_404(Post, pk=pk)
    post.add_user_sponsor(request.user)
    post.save()
    return redirect('post_detail', pk=post.pk)
    #return render(request, 'blog/add_sponsor_to_post.html', {})
    

@login_required
def set_user_informant(request, pk) :
    post = get_object_or_404(Post, pk=pk)
    post.set_user_informant(request.user)
    post.save()
    return redirect('post_detail', pk=post.pk)
    #return render(request, 'blog/add_informant_to_post.html', {})

@login_required
def post_detail_video (request, pk) :
    can_watch = False
    post = get_object_or_404(Post, pk=pk)

    if (str(request.user) == str(post.user_informant)) :
        can_watch = True

    sponsors = []
    if (post.user_sponsors != None) :
        sponsors = json.loads(post.user_sponsors)

    for sponsor in sponsors :
        if (str(sponsor) == str(request.user)) :
            can_watch = True
            break

    if (post.user_informant == None) :
        can_watch = False

    if (can_watch) :
        return render(request, 'blog/post_detail_video.html', {'title': post.title, 'info' : post.user_informant})
    else :
        return redirect('post_detail', pk=post.pk)
    
