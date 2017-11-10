# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.shortcuts import render, redirect, reverse, render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import *
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login as auth_login, authenticate

from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from grumblr.forms import *
import datetime
from grumblr.models import *
from django.core.mail import send_mail, EmailMessage
from mimetypes import guess_type
# Create your views here.

@login_required
def home(request):
    posts = Post.objects.all().order_by('-time')
    return render(request, 'grumblr/index.html', {'posts':posts})

def login(request):
    context = {}
    if request.user and request.user.is_authenticated():
        return redirect('home')
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'grumblr/login.html', context)
    form = LoginForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'grumblr/login.html', context)
    loginUser = authenticate(username=form.cleaned_data['username'],
                             password=form.cleaned_data['password'])
    auth_login(request, loginUser)
    return redirect('login')

@login_required
def post(request):
    errors = []
    if not 'post' in request.POST or not request.POST['post']:
        print('post FAIL')
        errors.append('must enter something to post')
    else:
        form = PostForm(request)
        form.text = request.POST['post']
        if form.is_valid:
            newPost = Post(text=request.POST['post'], user=request.user, time=datetime.datetime.now())
            print('post SUCCESS!', newPost.text)
            newPost.save()
        else:
            errors.append(newPost.errors)
    posts = Post.objects.all().order_by('-time')
    context = {'posts':posts, 'errors':errors}

    return render(request, 'grumblr/index.html', context)

def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'grumblr/register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        print('form is not valid')
        return render(request, 'grumblr/register.html', context)

    newUser = User.objects.create_user(username=request.POST['username'],
                                       first_name=request.POST['firstname'],
                                       last_name = request.POST['lastname'],
                                       password=request.POST['password1'],
                                       email = request.POST['email'])
    newUser.isActive = False
    newUser.save()
    newProfile = Grumbler(owner=newUser,
                          first_name=request.POST['firstname'],
                          last_name=request.POST['lastname'],
                          email=request.POST['email'])
    newProfile.save()
    # newUser = authenticate(username = form.cleaned_data['username'], \
    #                                    password=form.cleaned_data['password1'])
    # auth_login(request, newUser)
    token = default_token_generator.make_token(newUser)
    email_body = '''
    Welcome to Grumblr: a small blogging website. Please click the link below to finish registration of your account:
    
    http://%s%s
    ''' % (request.get_host(), reverse('activate', args=(newUser.username, token)))
    send_mail(subject='Verify your email --- Grumblr',
              message= email_body,
              from_email='xiaok@andrew.cmu.edu',
              recipient_list=[newUser.email])
    context['email'] = newUser.email
    return render(request, 'grumblr/confirm.html',context)

@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        myProfile = Grumbler.objects.get(owner = user)
    except ObjectDoesNotExist:
        raise Http404
    posts = Post.objects.filter(user=user).order_by('-time')
    context = {'posts':posts, 'profile' : myProfile}
    if not Follow.objects.filter(me=request.user,
                                 follow=user):
        context['follow'] = 'follow'
    else:
        context['follow'] = 'unfollow'
    return render(request, 'grumblr/profile.html', context)

@login_required
def followed(request):
    context = {}
    follow_list = []
    follower = Follow.objects.filter(me = request.user)
    for f in follower:
        follow_list.append(f.follow)
    context['posts'] = Post.objects.filter(user__in=follow_list).order_by('-time')
    return render(request, 'grumblr/followed.html', context)

@login_required
def edit(request):
    context = {}
    try:
        toEdit = Grumbler.objects.get(owner = request.user)
    except ObjectDoesNotExist:
        toEdit = Grumbler.objects.create(owner=request.user)
        toEdit.save()
    toEdit = Grumbler.objects.get(owner=request.user)
    if request.method == 'GET':
        context = {'form':EntryForm(instance=toEdit)}
        context['reset'] = PasswordReset()
        return render(request, 'grumblr/edit.html', context)
    if 'edit' in request.POST:
        form = EntryForm(request.POST, request.FILES, instance=toEdit)
        context['form'] = form
        if not form.is_valid():
            return render(request, 'grumblr/edit.html', context)
        user = User.objects.get(username=request.user.username)
        user.last_name = toEdit.last_name
        user.first_name = toEdit.first_name
        user.save()
        form.save()
    else:
        user = User.objects.get(username = request.user.username)
        user.set_password(request.POST['password1'])
        user.save()
        auth_login(request, user)

    return redirect('edit')

@login_required
def get_photo(request, username):
    if username == 'default':
        HttpResponse("/media/photos/default-user.png")
    entry = get_object_or_404(Grumbler, owner=User.objects.get(username=username))
    if not entry.picture:
        print('no pictures found')
        raise Http404
    return HttpResponse(entry.picture)

@login_required
def follow(request, username):
    user = User.objects.get(username = username)
    newFollow = Follow(me=request.user, follow=user)
    newFollow.save()
    return profile(request, username)

@login_required
def unfollow(request, username):
    user = User.objects.get(username = username)
    deleteFollow = Follow.objects.get(me=request.user, follow=user)
    deleteFollow.delete()
    return profile(request, username)


def activate(request, username, token):
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return render(request, 'grumblr/invalid_auth.html')

    if user and default_token_generator.check_token(user=user, token=token):
        user.is_active = True
        user.save()
        auth_login(request, user)
        return redirect('edit')
    else:
        return render(request, 'grumblr/invalid_auth.html')

def forgot(request):
    context = {}
    if request.method == 'GET':
        context['form'] = Email()
        return render(request, 'grumblr/forgot.html', context)
    user = Grumbler.objects.get(email=request.POST['email']).owner
    if not user:
        context['error'] = 'could not find that email'
        context['form'] = Email()
        return render(request, 'grumblr/forgot.html', context)
    token = default_token_generator.make_token(user)
    email_body = '''
        Welcome to Grumblr: a small blogging website. Please click the link below to reset password:

        http://%s%s
        ''' % (request.get_host(), reverse('activate', args=(user.username, token)))
    send_mail(subject='Reset Password --- Grumblr',
              message=email_body,
              from_email='xiaok@andrew.cmu.edu',
              recipient_list=[request.POST['email']])
    context['email'] = request.POST['email']
    return render(request, 'grumblr/confirm.html', context)

@login_required
def update(request, time="1970-01-01T00:00+00:00"):
    max_time = Post.get_max_time()
    items = Post.get_items(time)
    context = {"max_time": max_time, "items": items}
    return render(request, 'grumblr/posts.json', context)

@login_required
def get_comments(request, postid):
    try:
        post = Post.objects.get(id__exact=postid)
    except ObjectDoesNotExist:
        raise Http404
    try:
        comments = Comment.get_comments(post=post)
    except ObjectDoesNotExist:
        render(request, 'grumblr/posts.json', {})
    context = {"items":comments}
    return render(request, 'grumblr/posts.json', context)

@login_required
def comment_input(request, postid):
    context = {}
    if request.method == 'GET':
        context['user'] = request.user
        context['postid'] = postid
        return render(request, 'grumblr/comment_input.html', context)
    try:
        post = Post.objects.get(id__exact=postid)
        text = request.POST['text']
    except ObjectDoesNotExist:
        return render(request, 'grumblr/comment_input.html', context)
    newCommentForm = C
    if newCommentForm.is_valid():
        newComment = Comment(post=post, commenter=request.user, text=text)
        newComment.save()
        context = {'post':newComment}
        context['postid'] = postid
        return render(request, 'grumblr/comment.html', context)
    print(newCommentForm.errors)
    # return render(request, 'grumblr/errors.json', {'error': newCommentForm.errors})
    context['user'] = request.user
    context['postid'] = postid
    context['errors'] = newCommentForm.errors
    return render(request, 'grumblr/comment_input.html', context)