from django.conf.urls import url
from profiles import views

urlpatterns = [
    url(r'^profile/(?P<username>[\w\-]+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^add_post/$', views.AddPostView.as_view(), name='add_post'),
    url(r'^edit_post/$', views.EditPostView.as_view(), name='edit_post'),
    url(r'^remove_post/$', views.RemovePostView.as_view(), name='remove_post'),
    url(r'^add_comment/$', views.AddCommentView.as_view(), name='add_comment'),
    url(r'^edit_comment/$', views.EditCommentView.as_view(), name='edit_comment'),
    url(r'^remove_comment/$', views.RemoveCommentView.as_view(), name='remove_comment'),
    url(r'^like/$', views.LikeView.as_view(), name='like_post'),
]
