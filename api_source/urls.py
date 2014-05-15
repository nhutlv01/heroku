from api_source import views

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^photos/(?P<photo_id>\d+)$', views.getOrDeletePhoto),

    url(r'^photos$', views.postPhoto),

    url(r'^photos/(?P<photo_id>\d+)/likes$', views.likeAction),

    url(r'^photos/(?P<photo_id>\d+)/comments$', views.getOrPostComment),

    url(r'^photos/(?P<photo_id>\d+)/comments/(?P<comment_id>\d+)$', views.deleteComment),

    url(r'^users/(?P<user_id>\d+)$', views.getUser),

    url(r'^users/search$', views.searchUser),

    url(r'^users/(?P<user_id>\d+)/follows$', views.follow),

    url(r'^users/(?P<user_id>\d+)/follows-by$', views.followBy),

    url(r'^users/(?P<target_id>\d+)/relationship$', views.relationShipAction),

    url(r'^users/self/feed$', views.getFeed),

)
