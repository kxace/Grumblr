# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render, render_to_response


# Create your models here.



class Post(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=42)
    time = models.DateTimeField(null=True, blank=True, auto_now=True)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.text
    # get all recent addition of the posts
    @staticmethod
    def get_items(time="1970-01-01T00:00+00:00"):
        return Post.objects.filter(time__gt=time).distinct().order_by('time')
    # get last updated post
    @staticmethod
    def get_max_time():
        return Post.objects.all().aggregate(Max('time'))['time__max'] \
               or "1970-01-01T00:00+00:00"

    @property
    def html(self):
        return render_to_response(template_name='grumblr/post.html', context={'post':self}).content

class Grumbler(models.Model):
    owner = models.ForeignKey(User)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=20, blank=True)
    email = models.EmailField(max_length=50, default="")
    bio = models.CharField(max_length = 420, default="", blank=True)
    picture = models.ImageField(upload_to="photos/", blank=True)
    def __unicode__(self):
        return self.first_name + " " + self.last_name

class Follow(models.Model):
    me = models.ForeignKey(User, related_name='follower')
    follow = models.ForeignKey(User, related_name='followed')

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='post', null=True)
    commenter = models.ForeignKey(User, related_name='commenter')
    text = models.CharField(max_length=250)
    time = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_comments(post):
        return Comment.objects.filter(post__exact=post).order_by('time')

    @property
    def html(self):
        return render_to_response(template_name='grumblr/comment.html', context={'post': self}).content
