from django.conf.urls import patterns, url, include

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^v1/', include('api_source.urls')),
    url(r'^authentication/', include('authentication.urls')),
)