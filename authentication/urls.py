from django.conf.urls import patterns, url

urlpatterns = patterns('authentication.views',
    url(r'^signup$', 'signup'),
    url(r'^logout$', 'logout'),
    url(r'^login$', 'login'),
    url(r'^password$', 'changePassword'),
)