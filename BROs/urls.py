"""BROs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from profiles import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register_profile/$', views.RegisterProfileView.as_view(), name='register_profile'),
    url(r'^profile/(?P<username>[\w\-]+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^accounts/register/$', views.MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^add_post/$', views.AddPostView.as_view(), name='add_post'),
    url(r'^edit_post/$', views.EditPostView.as_view(), name='edit_post'),
    url(r'^remove_post/$', views.RemovePostView.as_view(), name='remove_post'),
    url(r'^add_comment/$', views.AddCommentView.as_view(), name='add_comment'),
    url(r'^edit_comment/$', views.EditCommentView.as_view(), name='edit_comment'),
    url(r'^remove_comment/$', views.RemoveCommentView.as_view(), name='remove_comment'),
    url(r'^like_post/$', views.LikePostView.as_view(), name='like_post'),
    url(r'^like_comment/$', views.LikeCommentView.as_view(), name='like_comment'),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
