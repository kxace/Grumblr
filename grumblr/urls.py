from django.conf.urls import url, include
from grumblr import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login, name='login'),
    url(r'^post$', views.post, name='post'),
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^photo/(?P<username>\w+)$', views.get_photo, name='photo'),
    url(r'^profile/(?P<username>\w+)/$', views.profile, name='profile'),
    url(r'^admin/', admin.site.urls),
    url(r'^followed$', views.followed, name='followed'),
    url(r'^edit$', views.edit, name='edit'),
    url(r'^follow/(?P<username>\w+)$', views.follow, name='follow'),
    url(r'^unfollow/(?P<username>\w+)$', views.unfollow, name='unfollow'),
    url(r'^activate/(?P<username>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^forgot$', views.forgot, name='forgot'),
    url(r'^index/get-update/(?P<time>.+)$', views.update, name='update'),
    url(r'^index/get-update/$', views.update),
    url(r'^get-comments/(?P<postid>\w+)$', views.get_comments, name='comments'),
    url(r'^comment-input/(?P<postid>\w+)$$', views.comment_input, name='comment-input'),
url(r'comment-input/(?P<postid>\w+)$$', views.comment_input),
]
