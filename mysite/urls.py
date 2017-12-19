from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views

from blog import views as core_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('blog.urls')),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout', kwargs={'next_page': '/'}),
    url(r'^signup/$', core_views.signup, name='signup'),
]
