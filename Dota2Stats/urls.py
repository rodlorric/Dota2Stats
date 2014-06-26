from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^stats/', include('stats.urls', namespace = "player")),
    url(r'', include('social_auth.urls')),
    url(r'^login/$', RedirectView.as_view(url ='/login/steam')),
)
